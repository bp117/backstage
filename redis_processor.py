"""
Redis processor - real-time trace processing from Redis streams.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import redis.asyncio as redis

from guardrails_eval.utils.config_loader import ConfigLoader
from guardrails_eval.utils.trace_parser import TraceParser
from guardrails_eval.executor.guardrails_executor import GuardrailsExecutor
from guardrails_eval.processors.result_processor import ResultProcessor

logger = logging.getLogger(__name__)


class RedisProcessor:
    """
    Processes traces from Redis in real-time.
    Subscribes to Redis channel for span messages and assembles traces.
    """
    
    def __init__(
        self,
        redis_config: Dict[str, Any],
        mongodb_config: Dict[str, Any],
        kafka_config: Dict[str, Any],
        arize_config: Optional[Dict[str, Any]],
        agent_card: Dict[str, Any]
    ):
        """
        Initialize Redis processor.
        
        Args:
            redis_config: Redis configuration
            mongodb_config: MongoDB configuration
            kafka_config: Kafka configuration
            arize_config: Arize configuration (optional)
            agent_card: Agent card configuration
        """
        self.redis_config = redis_config
        self.agent_card = agent_card
        self.runtime_id = agent_card.get("runtime_id")
        
        # Redis connection
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        
        # Trace assembly
        self.trace_buffer: Dict[str, List[Dict]] = {}  # trace_id -> spans
        self.trace_metadata: Dict[str, Dict] = {}  # trace_id -> metadata
        
        # Processors
        self.executor = GuardrailsExecutor(agent_card)
        self.result_processor = ResultProcessor(
            mongodb_uri=mongodb_config["uri"],
            database_name=mongodb_config["database"],
            kafka_config=kafka_config,
            arize_config=arize_config,
            task_registry_collection=mongodb_config.get("task_registry_collection", "TaskRegistry"),
            trace_exports_collection=mongodb_config.get("trace_exports_collection", "trace_exports")
        )
        
        # Worker management
        self.num_workers = redis_config.get("num_workers", 5)
        self.running = False
        self.worker_tasks: List[asyncio.Task] = []
    
    async def connect(self):
        """Connect to Redis"""
        try:
            redis_url = f"redis://{self.redis_config['host']}:{self.redis_config['port']}"
            password = self.redis_config.get("password")
            if password:
                redis_url = f"redis://:{password}@{self.redis_config['host']}:{self.redis_config['port']}"
            
            self.redis_client = await redis.from_url(
                redis_url,
                decode_responses=True,
                db=self.redis_config.get("db", 0)
            )
            
            logger.info(
                f"Connected to Redis: {self.redis_config['host']}:{self.redis_config['port']}"
            )
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def start(self):
        """Start processing traces from Redis"""
        self.running = True
        
        # Connect to Redis
        await self.connect()
        
        # Subscribe to channel
        channel = f"spans:{self.runtime_id}"
        self.pubsub = self.redis_client.pubsub()
        await self.pubsub.subscribe(channel)
        
        logger.info(f"Subscribed to Redis channel: {channel}")
        
        # Start worker pool
        for i in range(self.num_workers):
            task = asyncio.create_task(self._worker(i))
            self.worker_tasks.append(task)
        
        logger.info(f"Started {self.num_workers} Redis processor workers")
        
        # Start listening for messages
        await self._listen_for_spans()
    
    async def _listen_for_spans(self):
        """Listen for span messages from Redis"""
        try:
            async for message in self.pubsub.listen():
                if not self.running:
                    break
                
                if message["type"] == "message":
                    try:
                        span_data = json.loads(message["data"])
                        await self._handle_span(span_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse span JSON: {e}")
                    except Exception as e:
                        logger.error(f"Error handling span: {e}")
        
        except asyncio.CancelledError:
            logger.info("Redis listener cancelled")
        except Exception as e:
            logger.error(f"Error in Redis listener: {e}")
    
    async def _handle_span(self, span_data: Dict[str, Any]):
        """
        Handle incoming span message.
        
        Args:
            span_data: Span data from Redis
        """
        trace_id = span_data.get("context", {}).get("trace_id")
        
        if not trace_id:
            logger.warning("Received span without trace_id")
            return
        
        # Filter: only process LLM and TOOL spans
        span_kind = span_data.get("span_kind")
        if span_kind not in ["LLM", "TOOL"]:
            logger.debug(f"Ignoring span kind: {span_kind}")
            return
        
        # Add to trace buffer
        if trace_id not in self.trace_buffer:
            self.trace_buffer[trace_id] = []
        
        self.trace_buffer[trace_id].append(span_data)
        
        # Check if trace is complete
        if self._is_trace_complete(trace_id, span_data):
            await self._process_complete_trace(trace_id)
    
    def _is_trace_complete(self, trace_id: str, span_data: Dict[str, Any]) -> bool:
        """
        Determine if trace is complete.
        
        Simple heuristic: trace is complete when we receive a span with status "OK"
        and it's the root span (parent_id is None or empty).
        
        You may need to adjust this logic based on your trace format.
        """
        parent_id = span_data.get("parent_id")
        status = span_data.get("status", {}).get("status_code")
        
        # Root span with OK status indicates trace completion
        return (parent_id is None or parent_id == "") and status == "OK"
    
    async def _process_complete_trace(self, trace_id: str):
        """
        Process a complete trace.
        
        Args:
            trace_id: Trace identifier
        """
        try:
            spans = self.trace_buffer.pop(trace_id, [])
            
            if not spans:
                logger.warning(f"No spans found for trace {trace_id}")
                return
            
            logger.info(f"Processing complete trace {trace_id} ({len(spans)} spans)")
            
            # Parse trace
            parsed_trace = TraceParser.parse_spans_from_json(spans)
            
            # Extract user prompt and model response
            user_prompt, model_response = TraceParser.extract_user_prompt_and_response(
                parsed_trace.get("llm_spans", [])
            )
            
            # Run guardrails evaluation
            evaluation_result = await self.executor.evaluate(parsed_trace)
            
            # Save results with user prompt and model response
            await self.result_processor.save_evaluation_result(
                trace_id=trace_id,
                runtime_id=self.runtime_id,
                evaluation_result=evaluation_result,
                source_type="redis",
                source_reference=f"channel:spans:{self.runtime_id}",
                user_prompt=user_prompt,
                model_response=model_response
            )
            
            logger.info(
                f"Completed evaluation for trace {trace_id}: "
                f"{evaluation_result['overall_status']} "
                f"(breached: {evaluation_result['breached_status']})"
            )
            
        except Exception as e:
            logger.error(f"Error processing trace {trace_id}: {e}")
    
    async def _worker(self, worker_id: int):
        """Worker coroutine (placeholder for future enhancements)"""
        logger.info(f"Redis worker {worker_id} started")
        
        try:
            while self.running:
                await asyncio.sleep(1)  # Keep alive
        except asyncio.CancelledError:
            logger.info(f"Redis worker {worker_id} cancelled")
    
    async def stop(self):
        """Stop processing"""
        logger.info("Stopping Redis processor...")
        self.running = False
        
        # Cancel workers
        for task in self.worker_tasks:
            task.cancel()
        
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        # Unsubscribe and close connections
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        await self.result_processor.close()
        
        logger.info("Redis processor stopped")
