"""
HPOS processor - batch processing of CSV trace exports from S3.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
from pathlib import Path
from io import BytesIO, StringIO
import boto3
from botocore.exceptions import ClientError

from guardrails_eval.models.mongodb_models import ProcessingStatus
from guardrails_eval.utils.trace_parser import TraceParser
from guardrails_eval.utils.goal_inference import GoalInference
from guardrails_eval.executor.guardrails_executor import GuardrailsExecutor
from guardrails_eval.processors.result_processor import ResultProcessor
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


class HPOSProcessor:
    """
    Processes trace exports from HPOS (CSV files).
    Polls TraceExports collection for pending files, processes them in batches.
    """
    
    def __init__(
        self,
        hpos_config: Dict[str, Any],
        mongodb_config: Dict[str, Any],
        kafka_config: Dict[str, Any],
        arize_config: Optional[Dict[str, Any]],
        agent_card: Dict[str, Any]
    ):
        """
        Initialize HPOS processor.
        
        Args:
            hpos_config: HPOS configuration with S3 settings
            mongodb_config: MongoDB configuration
            kafka_config: Kafka configuration
            arize_config: Arize configuration (optional)
            agent_card: Agent card configuration
        """
        self.hpos_config = hpos_config
        self.agent_card = agent_card
        self.runtime_id = agent_card.get("runtime_id")
        
        # MongoDB connection
        self.client = AsyncIOMotorClient(mongodb_config["uri"])
        self.db = self.client[mongodb_config["database"]]
        self.trace_exports = self.db[mongodb_config.get("trace_exports_collection", "trace_exports")]
        
        # S3 configuration
        self.use_s3 = hpos_config.get("use_s3", True)
        if self.use_s3:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=hpos_config.get("aws_access_key_id"),
                aws_secret_access_key=hpos_config.get("aws_secret_access_key"),
                region_name=hpos_config.get("aws_region", "us-east-1")
            )
            self.s3_bucket = hpos_config.get("s3_bucket")
            logger.info(f"S3 storage enabled: bucket={self.s3_bucket}")
        else:
            # Fallback to local filesystem
            self.csv_directory = Path(hpos_config.get("csv_directory", "./hpos_exports"))
            logger.info(f"Local filesystem storage: directory={self.csv_directory}")
        
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
        
        # Goal inference
        self.goal_inference = GoalInference(agent_card)
        
        # Processing config
        self.poll_interval = hpos_config.get("poll_interval_seconds", 30)
        self.batch_size = hpos_config.get("batch_size", 10)
        
        # State
        self.running = False
        self.poll_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start polling and processing"""
        self.running = True
        logger.info(f"Starting HPOS processor (poll interval: {self.poll_interval}s)")
        
        # Start polling task
        self.poll_task = asyncio.create_task(self._poll_loop())
        
        logger.info("HPOS processor started")
    
    async def _poll_loop(self):
        """Main polling loop"""
        while self.running:
            try:
                await self._process_pending_exports()
                await asyncio.sleep(self.poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in HPOS poll loop: {e}")
                await asyncio.sleep(self.poll_interval)
    
    async def _process_pending_exports(self):
        """Process pending CSV exports"""
        try:
            # Query for pending exports
            cursor = self.trace_exports.find({
                "runtime_id": self.runtime_id,
                "status": ProcessingStatus.PENDING.value
            }).sort("created_at", 1).limit(self.batch_size)
            
            pending_exports = await cursor.to_list(length=self.batch_size)
            
            if not pending_exports:
                logger.debug("No pending exports found")
                return
            
            logger.info(f"Found {len(pending_exports)} pending exports")
            
            # Process each export
            for export_doc in pending_exports:
                await self._process_export(export_doc)
        
        except Exception as e:
            logger.error(f"Error querying pending exports: {e}")
    
    async def _download_csv_from_s3(self, s3_location: str) -> pd.DataFrame:
        """
        Download CSV file from S3.
        
        Args:
            s3_location: S3 URI (s3://bucket/key) or S3 key
            
        Returns:
            DataFrame with CSV contents
        """
        try:
            # Parse S3 location
            if s3_location.startswith("s3://"):
                # Format: s3://bucket/key
                parts = s3_location[5:].split("/", 1)
                bucket = parts[0]
                key = parts[1] if len(parts) > 1 else ""
            else:
                # Assume it's just the key, use configured bucket
                bucket = self.s3_bucket
                key = s3_location
            
            logger.debug(f"Downloading from S3: bucket={bucket}, key={key}")
            
            # Download file content
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            csv_content = response['Body'].read()
            
            # Parse CSV
            df = pd.read_csv(BytesIO(csv_content))
            logger.info(f"Downloaded CSV from S3: {len(df)} rows")
            
            return df
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise FileNotFoundError(f"S3 file not found: {s3_location}")
            elif error_code == 'NoSuchBucket':
                raise FileNotFoundError(f"S3 bucket not found: {bucket}")
            else:
                raise Exception(f"S3 error ({error_code}): {e}")
    
    async def _load_csv_file(self, csv_filename: str) -> pd.DataFrame:
        """
        Load CSV file from S3 or local filesystem.
        
        Args:
            csv_filename: S3 location or local filename
            
        Returns:
            DataFrame with CSV contents
        """
        if self.use_s3:
            # Download from S3
            return await self._download_csv_from_s3(csv_filename)
        else:
            # Load from local filesystem
            csv_path = self.csv_directory / csv_filename
            
            if not csv_path.exists():
                raise FileNotFoundError(f"CSV file not found: {csv_path}")
            
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded CSV from local filesystem: {len(df)} rows")
            return df

    async def _process_export(self, export_doc: Dict[str, Any]):
        """
        Process a single CSV export from S3 or local storage.
        
        Args:
            export_doc: TraceExports document with csv_filename containing S3 location
        """
        csv_filename = export_doc["csv_filename"]
        
        try:
            logger.info(f"Processing CSV export: {csv_filename}")
            
            # Update status to RUNNING
            await self.result_processor.update_trace_export_status(
                csv_filename=csv_filename,
                status=ProcessingStatus.RUNNING
            )
            
            # Load CSV file from S3 or local filesystem
            df = await self._load_csv_file(csv_filename)
            logger.info(f"Loaded CSV with {len(df)} rows")
            
            # Group by trace_id
            traces = TraceParser.group_csv_by_trace_id(df.to_dict('records'))
            logger.info(f"Found {len(traces)} unique traces in CSV")
            
            # Process each trace
            processed_count = 0
            failed_count = 0
            
            for trace_id, trace_data in traces.items():
                try:
                    # Parse spans from CSV rows
                    spans = TraceParser.parse_spans_from_csv(trace_data)
                    
                    # Extract user prompt early for goal inference
                    temp_llm_spans = [s for s in spans if s.attributes.get("openinference.span.kind") == "LLM"]
                    user_prompt, model_response = TraceParser.extract_user_prompt_and_response(temp_llm_spans)
                    
                    # Infer goal from user prompt and tools
                    tool_calls = []
                    for s in spans:
                        if s.attributes.get("openinference.span.kind") == "TOOL":
                            # Extract tool name from input.value (e.g., "search_and_summarize with query: ...")
                            input_value = s.attributes.get("input.value", "")
                            tool_name = input_value.split(" with ")[0].strip() if " with " in input_value else input_value.strip()
                            if not tool_name:
                                tool_name = s.name  # Fallback to span name if extraction fails
                            tool_calls.append({"tool_name": tool_name})
                    inferred_goal = self.goal_inference.infer_goal(
                        user_prompt=user_prompt or "",
                        tool_calls=tool_calls,
                        llm_spans=temp_llm_spans
                    )
                    
                    logger.info(f"Inferred goal for trace {trace_id}: {inferred_goal}")
                    
                    # Parse complete trace with filtering and metadata (including inferred goal)
                    parsed_trace = TraceParser.parse_trace(
                        spans=spans,
                        trace_id=trace_id,
                        runtime_id=self.runtime_id,
                        goal_name=inferred_goal  # Use inferred goal
                    )
                    
                    # Convert ParsedTrace to dictionary for evaluation
                    trace_dict = parsed_trace.model_dump()
                    
                    # Run evaluation
                    evaluation_result = await self.executor.evaluate(trace_dict)
                    
                    # Save results with user prompt and model response
                    await self.result_processor.save_evaluation_result(
                        trace_id=trace_id,
                        runtime_id=self.runtime_id,
                        evaluation_result=evaluation_result,
                        source_type="hpos_csv",
                        source_reference=csv_filename,
                        user_prompt=user_prompt,
                        model_response=model_response
                    )
                    
                    processed_count += 1
                    
                    logger.debug(
                        f"Processed trace {trace_id}: {evaluation_result['overall_status']}"
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to process trace {trace_id}: {e}")
                    failed_count += 1
            
            # Update status to COMPLETED
            await self.result_processor.update_trace_export_status(
                csv_filename=csv_filename,
                status=ProcessingStatus.COMPLETED
            )
            
            logger.info(
                f"Completed processing {csv_filename}: "
                f"{processed_count} traces processed, {failed_count} failed"
            )
            
        except Exception as e:
            logger.error(f"Failed to process CSV export {csv_filename}: {e}")
            
            # Update status to FAILED
            await self.result_processor.update_trace_export_status(
                csv_filename=csv_filename,
                status=ProcessingStatus.FAILED,
                error_message=str(e)
            )
    
    async def stop(self):
        """Stop processing"""
        logger.info("Stopping HPOS processor...")
        self.running = False
        
        # Cancel poll task
        if self.poll_task:
            self.poll_task.cancel()
            try:
                await self.poll_task
            except asyncio.CancelledError:
                pass
        
        # Close connections
        self.client.close()
        await self.result_processor.close()
        
        logger.info("HPOS processor stopped")
