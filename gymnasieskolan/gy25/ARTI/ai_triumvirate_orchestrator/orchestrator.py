import asyncio
import json
import time
import uuid
from typing import Optional, Dict, Any

import structlog

from .core import ConsultRequest, ConsultResponse, ProviderAdapter, ConversationHistory
from .cost import CostTracker

# Configure structlog for structured logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

class TriumvirateOrchestrator:
    def __init__(
        self,
        architect_adapter: ProviderAdapter,
        engineer_adapter: ProviderAdapter,
        default_timeout: float = 30.0,
        max_retries: int = 3
    ):
        self.architect_adapter = architect_adapter
        self.engineer_adapter = engineer_adapter
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.conversation_history = ConversationHistory()
        self.cost_tracker = CostTracker()
    
    async def consult_and_wait(
        self,
        role: str,
        prompt: str,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        **kwargs
    ) -> ConsultResponse:
        """
        Core consultation helper with retry logic and validation.
        
        Args:
            role: "architect" or "engineer"
            prompt: The consultation prompt
            timeout: Override default timeout
            retries: Override default max_retries
            **kwargs: Additional ConsultRequest fields
        """
        timeout = timeout or self.default_timeout
        retries = retries or self.max_retries
        
        adapter = self._get_adapter(role)
        request_id = str(uuid.uuid4())
        conversation_id = self.conversation_history.get_conversation_id()
        
        request = ConsultRequest(
            request_id=request_id,
            conversation_id=conversation_id,
            role=role,
            prompt=prompt,
            max_tokens=kwargs.get('max_tokens', 4096),
            timeout=timeout,
            **{k: v for k, v in kwargs.items() if k != 'max_tokens'}
        )
        
        last_error = None
        for attempt in range(retries):
            try:
                start_time = time.time()
                
                # Perform the consultation
                response = await adapter.consult(request)
                
                latency = (time.time() - start_time) * 1000
                logger.info(
                    "consultation.response_received",
                    request_id=request_id,
                    latency_ms=latency,
                    tokens_used=response.tokens_used,
                    model_name=response.model_name,
                    status=response.status
                )
                
                # Update conversation history
                self.conversation_history.add_entry(
                    role=role,
                    content=response.content,
                    metadata={
                        "request_id": request_id,
                        "tokens_used": response.tokens_used,
                        "latency_ms": latency,
                        "status": response.status,
                        "error_message": response.error_message
                    }
                )
                
                if response.status == "error":
                    raise RuntimeError(f"Consultation failed with status 'error': {response.error_message}")

                # Record the cost of the successful consultation
                self.cost_tracker.record_consultation(
                    conversation_id=conversation_id,
                    token_usage=response.token_usage,
                    model_name=response.model_name
                )

                return response
                
            except (TimeoutError, ConnectionError, RuntimeError) as e:
                last_error = e
                logger.warning(
                    "consultation.attempt_failed",
                    request_id=request_id, 
                    error=str(e),
                    attempt=attempt + 1
                )
                if attempt < retries - 1:
                    backoff = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(backoff)
                continue
        
        # All retries exhausted
        logger.error(
            "consultation.failed_after_retries",
            request_id=request_id, 
            retries=retries,
            last_error=str(last_error)
        )
        raise RuntimeError(f"Consultation failed after {retries} attempts") from last_error
    
    def _get_adapter(self, role: str) -> ProviderAdapter:
        if role == "architect":
            return self.architect_adapter
        elif role == "engineer":
            return self.engineer_adapter
        else:
            raise ValueError(f"Unknown role: {role}")

    async def generate_api_endpoint(self, user_request: str) -> Dict[str, Any]:
        """End-to-end workflow: design an API endpoint and then implement it."""
        
        # Step 1: Architect designs the API
        architect_prompt = f"""
        Design a REST API endpoint based on this requirement:
        {user_request}
        
        Provide:
        1. Endpoint path and HTTP method
        2. Request/response data models
        3. Success criteria for implementation
        
        Format the response as a single JSON object with keys: endpoint, method, request_model, response_model, success_criteria.
        """
        
        logging.info(f"Starting API generation workflow for: {user_request}")
        architect_response = await self.consult_and_wait(
            role="architect",
            prompt=architect_prompt,
            request_type="api_design"
        )
        
        if architect_response.status != "success":
            raise RuntimeError(f"Architect consultation failed: {architect_response.error_message}")
        
        try:
            design = json.loads(architect_response.content)
            logging.info(f"Architect provided design: {design}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse architect's design as JSON: {e}") from e

        # Basic validation of the design
        required_keys = ["endpoint", "method", "response_model"]
        if not all(key in design for key in required_keys):
            raise ValueError(f"Architect's design is missing required keys: {required_keys}")

        # Step 2: Engineer implements the design
        engineer_prompt = f"""
        Implement this API endpoint design using FastAPI:
        {json.dumps(design, indent=2)}
        
        Generate complete, runnable Python code including:
        - Pydantic models for the request and response.
        - The FastAPI route handler function.
        - All necessary imports.
        """
        
        engineer_response = await self.consult_and_wait(
            role="engineer",
            prompt=engineer_prompt,
            request_type="code_generation",
            context={"design": design} # Pass the design as context
        )
        
        if engineer_response.status != "success":
            raise RuntimeError(f"Engineer consultation failed: {engineer_response.error_message}")
        
        logging.info("Successfully generated API endpoint code.")
        return {
            "design": design,
            "code": engineer_response.content,
            "conversation_id": self.conversation_history.get_conversation_id()
        }
