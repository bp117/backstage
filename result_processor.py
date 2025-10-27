"""
Result processor - saves evaluation results to MongoDB, sends Kafka notifications, and exports to Arize.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from guardrails_eval.models.mongodb_models import TaskRegistryRecord, TraceExport, ProcessingStatus
from guardrails_eval.utils.kafka_notifier import get_kafka_notifier
from guardrails_eval.exporters.arize_exporter import ArizeExporter

logger = logging.getLogger(__name__)


class ResultProcessor:
    """
    Processes guardrail evaluation results:
    - Saves to TaskRegistry collection
    - Sends Kafka notifications for breaches
    - Exports to Arize for observability
    - Updates processor metrics
    """
    
    def __init__(
        self, 
        mongodb_uri: str, 
        database_name: str, 
        kafka_config: Dict[str, Any],
        arize_config: Optional[Dict[str, Any]] = None,
        task_registry_collection: str = "TaskRegistry",
        trace_exports_collection: str = "trace_exports"
    ):
        """
        Initialize result processor.
        
        Args:
            mongodb_uri: MongoDB connection URI
            database_name: Database name
            kafka_config: Kafka configuration
            arize_config: Arize configuration (optional)
            task_registry_collection: TaskRegistry collection name
            trace_exports_collection: TraceExports collection name
        """
        self.client = AsyncIOMotorClient(mongodb_uri)
        self.db = self.client[database_name]
        self.task_registry = self.db[task_registry_collection]
        self.trace_exports = self.db[trace_exports_collection]
        
        # Initialize Kafka notifier
        self.kafka_notifier = get_kafka_notifier(kafka_config)
        
        # Initialize Arize exporter
        self.arize_exporter = ArizeExporter(arize_config or {})
        logger.info(f"ResultProcessor initialized - Arize enabled: {self.arize_exporter.enabled}")
    
    async def save_evaluation_result(
        self,
        trace_id: str,
        runtime_id: str,
        evaluation_result: Dict[str, Any],
        source_type: str = "redis",
        source_reference: str = None,
        user_prompt: str = None,
        model_response: str = None
    ) -> str:
        """
        Save evaluation result to TaskRegistry.
        
        Args:
            trace_id: Trace identifier
            runtime_id: Runtime identifier
            evaluation_result: Complete evaluation result from GuardrailsExecutor
            source_type: Source of trace (redis, hpos_csv)
            source_reference: Reference to source (CSV filename, Redis key)
            user_prompt: User prompt extracted from trace
            model_response: Model response extracted from trace
            
        Returns:
            Inserted document ID
        """
        try:
            # Build TaskRegistry record
            record = TaskRegistryRecord(
                trace_id=trace_id,
                runtime_id=runtime_id,
                eval_status="completed",
                overall_status=evaluation_result["overall_status"],
                breached_status=evaluation_result["breached_status"],
                guardrail_results=evaluation_result["guardrail_results"],
                trace_metadata=evaluation_result.get("trace_metadata", {}),
                breach_details=evaluation_result.get("breach_details"),
                evaluation_time_ms=evaluation_result.get("evaluation_time_ms", 0),
                source_type=source_type,
                source_reference=source_reference,
                user_prompt=user_prompt,
                model_response=model_response,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Upsert (update if exists, insert if not)
            # Exclude _id field to let MongoDB generate it
            record_dict = record.model_dump(by_alias=True, exclude_none=True)
            if "_id" in record_dict and record_dict["_id"] is None:
                del record_dict["_id"]
            
            result = await self.task_registry.update_one(
                {"trace_id": trace_id},
                {"$set": record_dict},
                upsert=True
            )
            
            logger.info(
                f"Saved evaluation result for trace {trace_id} "
                f"(breached: {record.breached_status})"
            )
            
            # Send Kafka notification if breach detected
            if record.breached_status:
                await self.kafka_notifier.send_breach_notification(
                    trace_id=trace_id,
                    runtime_id=runtime_id,
                    breach_details=evaluation_result.get("breach_details", {}),
                    evaluation_result=evaluation_result
                )
                
                # Send breach alert to Arize
                await self.arize_exporter.export_breach_alert(
                    trace_id=trace_id,
                    runtime_id=runtime_id,
                    breach_details=evaluation_result.get("breach_details", {})
                )
            
            # Export evaluation result to Arize (async, non-blocking)
            await self.arize_exporter.export_evaluation_result(
                trace_id=trace_id,
                runtime_id=runtime_id,
                evaluation_result=evaluation_result,
                user_prompt=user_prompt,
                model_response=model_response,
                trace_metadata=evaluation_result.get("trace_metadata", {})
            )
            
            return str(result.upserted_id) if result.upserted_id else trace_id
            
        except Exception as e:
            logger.error(f"Failed to save evaluation result for trace {trace_id}: {e}")
            raise
    
    async def update_trace_export_status(
        self,
        csv_filename: str,
        status: ProcessingStatus,
        error_message: str = None
    ):
        """
        Update TraceExports record status (for HPOS processor).
        
        Args:
            csv_filename: CSV filename
            status: New status (running, completed, failed)
            error_message: Error message if failed
        """
        try:
            update_data = {
                "status": status.value,
                "updated_at": datetime.utcnow()
            }
            
            if status == ProcessingStatus.COMPLETED:
                update_data["completed_at"] = datetime.utcnow()
            elif status == ProcessingStatus.FAILED:
                update_data["error_message"] = error_message
            
            result = await self.trace_exports.update_one(
                {"csv_filename": csv_filename},
                {"$set": update_data}
            )
            
            logger.info(f"Updated TraceExports status for {csv_filename}: {status.value}")
            
        except Exception as e:
            logger.error(f"Failed to update TraceExports status for {csv_filename}: {e}")
            raise
    
    async def close(self):
        """Close connections"""
        self.client.close()
        self.kafka_notifier.close()
        await self.arize_exporter.close()
        logger.info("ResultProcessor closed")
