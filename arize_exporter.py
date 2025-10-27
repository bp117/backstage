"""
Arize exporter - sends guardrail evaluation results to Arize for observability.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import asyncio

logger = logging.getLogger(__name__)


class ArizeExporter:
    """
    Exports guardrail evaluation results to Arize for monitoring and visualization.
    
    Enables:
    - Real-time guardrail violation tracking
    - Trend analysis over time
    - Correlation with model performance
    - Production quality monitoring
    """
    
    def __init__(self, arize_config: Dict[str, Any]):
        """
        Initialize Arize exporter.
        
        Args:
            arize_config: Arize configuration with endpoint, api_key, space_id, project_id
        """
        self.endpoint = arize_config.get("endpoint", "")
        self.api_key = arize_config.get("api_key", "")
        self.space_id = arize_config.get("space_id", "")
        self.project_id = arize_config.get("project_id", "")
        
        self.enabled = bool(self.endpoint and self.api_key and self.space_id)
        
        if self.enabled:
            self.client = httpx.AsyncClient(
                base_url=self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            logger.info(f"ArizeExporter initialized - endpoint: {self.endpoint}")
        else:
            self.client = None
            logger.warning("ArizeExporter disabled - missing configuration")
    
    async def export_evaluation_result(
        self,
        trace_id: str,
        runtime_id: str,
        evaluation_result: Dict[str, Any],
        user_prompt: Optional[str] = None,
        model_response: Optional[str] = None,
        trace_metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Export guardrail evaluation results to Arize.
        
        Args:
            trace_id: Unique trace identifier
            runtime_id: Agent runtime identifier
            evaluation_result: Complete evaluation result
            user_prompt: User's input prompt
            model_response: Agent's response
            trace_metadata: Additional trace metadata
            
        Returns:
            True if export successful, False otherwise
        """
        if not self.enabled:
            logger.debug("Arize export skipped - not enabled")
            return False
        
        try:
            # Build Arize-compatible payload
            payload = self._build_arize_payload(
                trace_id=trace_id,
                runtime_id=runtime_id,
                evaluation_result=evaluation_result,
                user_prompt=user_prompt,
                model_response=model_response,
                trace_metadata=trace_metadata
            )
            
            # Send to Arize
            response = await self.client.post(
                "/api/v1/evaluations",
                json=payload
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Successfully exported evaluation for trace {trace_id} to Arize")
                return True
            else:
                logger.error(
                    f"Failed to export to Arize (status {response.status_code}): "
                    f"{response.text}"
                )
                return False
                
        except Exception as e:
            logger.error(f"Error exporting to Arize: {str(e)}", exc_info=True)
            return False
    
    def _build_arize_payload(
        self,
        trace_id: str,
        runtime_id: str,
        evaluation_result: Dict[str, Any],
        user_prompt: Optional[str],
        model_response: Optional[str],
        trace_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build Arize-compatible payload from evaluation results.
        
        Arize Payload Structure:
        - Trace information (ID, timestamp, runtime)
        - Predictions (user prompt, model response)
        - Actuals (guardrail results as ground truth)
        - Tags (breach status, overall status, goal)
        - Metrics (evaluation time, token counts, etc.)
        - Embeddings (optional, for semantic analysis)
        """
        metadata = trace_metadata or {}
        
        # Extract guardrail results for Arize
        guardrail_results = evaluation_result.get("guardrail_results", [])
        
        # Build evaluation scores (one per guardrail)
        evaluations = []
        for gr in guardrail_results:
            evaluations.append({
                "name": gr.get("guardrail_name", "unknown"),
                "score": 1.0 if gr.get("status") == "passed" else 0.0,
                "label": gr.get("status", "unknown"),
                "explanation": gr.get("message", ""),
                "metadata": gr.get("details", {})
            })
        
        # Build tags for filtering/grouping in Arize
        tags = {
            "runtime_id": runtime_id,
            "overall_status": evaluation_result.get("overall_status", "unknown"),
            "breached": str(evaluation_result.get("breached_status", False)),
            "goal": metadata.get("inferred_goal", "unknown"),
            "source": "guardrails_sdk",
            "version": "1.0"
        }
        
        # Add breach details as tags if present
        breach_details = evaluation_result.get("breach_details")
        if breach_details:
            tags["breach_count"] = str(len(breach_details.get("violations", [])))
            tags["breach_severity"] = breach_details.get("highest_severity", "unknown")
        
        # Build metrics for quantitative analysis
        metrics = {
            "evaluation_time_ms": evaluation_result.get("evaluation_time_ms", 0),
            "total_steps": metadata.get("total_steps", 0),
            "total_tokens": metadata.get("total_tokens", 0),
            "llm_calls": metadata.get("llm_calls", 0),
            "tool_calls": metadata.get("tool_calls", 0),
            "duration_ms": metadata.get("duration_ms", 0)
        }
        
        # Add per-guardrail pass/fail counts
        passed_count = sum(1 for gr in guardrail_results if gr.get("status") == "passed")
        failed_count = sum(1 for gr in guardrail_results if gr.get("status") == "failed")
        
        metrics["guardrails_passed"] = passed_count
        metrics["guardrails_failed"] = failed_count
        metrics["guardrails_total"] = len(guardrail_results)
        
        # Build Arize payload
        payload = {
            "space_id": self.space_id,
            "model_id": runtime_id,
            "model_version": "1.0",
            "prediction_id": trace_id,
            "prediction_timestamp": datetime.utcnow().isoformat() + "Z",
            
            # Prediction data (what the agent did)
            "prediction": {
                "prompt": user_prompt or "",
                "response": model_response or "",
                "metadata": metadata
            },
            
            # Actual data (guardrail results as ground truth)
            "actual": {
                "overall_status": evaluation_result.get("overall_status"),
                "breached": evaluation_result.get("breached_status", False)
            },
            
            # Evaluations (individual guardrail results)
            "evaluations": evaluations,
            
            # Tags for filtering
            "tags": tags,
            
            # Metrics for analysis
            "metrics": metrics,
            
            # Environment
            "environment": "production"  # or "development" based on config
        }
        
        return payload
    
    async def export_batch(
        self,
        evaluation_results: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Export multiple evaluation results in batch.
        
        Args:
            evaluation_results: List of evaluation result dictionaries
            
        Returns:
            Dictionary with success and failure counts
        """
        if not self.enabled:
            return {"success": 0, "failed": 0, "skipped": len(evaluation_results)}
        
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        # Process in parallel (with semaphore to limit concurrency)
        semaphore = asyncio.Semaphore(10)  # Max 10 concurrent requests
        
        async def export_one(eval_data: Dict[str, Any]):
            async with semaphore:
                success = await self.export_evaluation_result(
                    trace_id=eval_data.get("trace_id"),
                    runtime_id=eval_data.get("runtime_id"),
                    evaluation_result=eval_data.get("evaluation_result", {}),
                    user_prompt=eval_data.get("user_prompt"),
                    model_response=eval_data.get("model_response"),
                    trace_metadata=eval_data.get("trace_metadata")
                )
                return success
        
        # Execute all exports in parallel
        tasks = [export_one(eval_data) for eval_data in evaluation_results]
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes and failures
        for result in task_results:
            if isinstance(result, Exception):
                results["failed"] += 1
            elif result:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        logger.info(
            f"Batch export complete: {results['success']} succeeded, "
            f"{results['failed']} failed"
        )
        
        return results
    
    async def export_breach_alert(
        self,
        trace_id: str,
        runtime_id: str,
        breach_details: Dict[str, Any]
    ) -> bool:
        """
        Send high-priority breach alert to Arize.
        
        Args:
            trace_id: Trace identifier
            runtime_id: Runtime identifier
            breach_details: Breach details from evaluation
            
        Returns:
            True if alert sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            alert_payload = {
                "space_id": self.space_id,
                "alert_type": "guardrail_breach",
                "severity": breach_details.get("highest_severity", "medium"),
                "trace_id": trace_id,
                "runtime_id": runtime_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "violations": breach_details.get("violations", []),
                "message": f"Guardrail breach detected in trace {trace_id}",
                "metadata": breach_details
            }
            
            response = await self.client.post(
                "/api/v1/alerts",
                json=alert_payload
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Breach alert sent to Arize for trace {trace_id}")
                return True
            else:
                logger.warning(f"Failed to send breach alert to Arize: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending breach alert to Arize: {str(e)}")
            return False
    
    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
            logger.info("ArizeExporter closed")
