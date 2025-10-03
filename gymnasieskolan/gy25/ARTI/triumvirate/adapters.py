import asyncio
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .core import ConsultRequest, ConsultResponse, ProviderAdapter


class FileSystemAdapter(ProviderAdapter):
    """Provider adapter for interacting with the local filesystem."""

    def __init__(self, communication_dir: str = "./triumvirate_communications"):
        self.communication_dir = Path(communication_dir).resolve()
        self.requests_dir = self.communication_dir / "requests"
        self.responses_dir = self.communication_dir / "responses"

        self.requests_dir.mkdir(parents=True, exist_ok=True)
        self.responses_dir.mkdir(parents=True, exist_ok=True)

    async def consult(self, req: ConsultRequest) -> ConsultResponse:
        """Writes a request file and polls for a corresponding response file."""
        await self._send_request_file(req)
        return await self._receive_response_file(req.request_id, req.timeout)

    async def _send_request_file(self, req: ConsultRequest) -> str:
        """Saves the request to a JSON file atomically and returns the file path."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        request_filename = f"tcp_request_{req.request_id[:8]}_{timestamp}.json"
        request_path = self.requests_dir / request_filename
        temp_path = request_path.with_suffix('.tmp')

        tcp_request = {
            "header": {
                "protocol_version": req.schema_version,
                "request_id": req.request_id,
                "conversation_id": req.conversation_id,
                "timestamp": timestamp
            },
            "routing": {
                "source_agent": "Gemini", # This could be made dynamic
                "target_agent_role": req.role
            },
            "payload": {
                "type": req.request_type,
                "prompt": req.prompt,
                "system_prompt": req.system_prompt,
                "context": req.context or {},
                "specifications": {
                    "requirements": req.requirements or {},
                    "constraints": req.constraints or {},
                    "success_criteria": req.success_criteria or {}
                },
                "specific_questions": req.specific_questions or [],
                "response_format": req.expected_response_format or {}
            },
            "config": {
                "model_override": req.model_override,
                "api_params": req.api_params,
                "priority": req.priority,
                "urgency": req.urgency
            }
        }

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(tcp_request, f, indent=2)
            temp_path.replace(request_path)
            return str(request_path)
        except (IOError, json.JSONDecodeError) as e:
            if temp_path.exists():
                temp_path.unlink()
            raise ConnectionError(f"Failed to write request to filesystem: {e}") from e

    async def _receive_response_file(self, task_id: str, timeout: float) -> ConsultResponse:
        """Polls for a response file and returns its content."""
        start_time = time.time()
        task_id = response_id
        response_file: Optional[Path] = None

        while True:
            response_files = list(self.responses_dir.glob(f'tcp_response_{task_id[:8]}_*.json'))
            if response_files:
                response_file = max(response_files, key=lambda p: p.name)
                
                # Verify file write is complete by checking stable size
                if await self._is_file_complete(response_file):
                    break

            if (time.time() - start_time) > timeout:
                return ConsultResponse(
                    request_id=task_id,
                    content="",
                    model_name="",
                    tokens_used=0,
                    latency_ms=(time.time() - start_time) * 1000,
                    status="error",
                    error_message=f"Response file not found for task_id {task_id} within {timeout} seconds."
                )

            await asyncio.sleep(0.5)
        
        if not response_file:
             return ConsultResponse(
                request_id=task_id,
                content="",
                model_name="",
                tokens_used=0,
                latency_ms=(time.time() - start_time) * 1000,
                status="error",
                error_message=f"Response file not found for task_id {task_id} after polling."
            )

        try:
            with open(response_file, 'r', encoding='utf-8') as f:
                response_data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            return ConsultResponse(
                request_id=task_id,
                content="",
                model_name="",
                tokens_used=0,
                latency_ms=(time.time() - start_time) * 1000,
                status="error",
                error_message=f"Failed to read or parse response file {response_file}: {e}"
            )

        # Basic validation and extraction
        if response_data.get("task_id") != task_id:
            return ConsultResponse(
                request_id=task_id,
                content=json.dumps(response_data),
                model_name=response_data.get("responder", "Unknown"),
                tokens_used=response_data.get("diagnostics", {}).get("tokens_used", 0),
                latency_ms=(time.time() - start_time) * 1000,
                status="error",
                error_message="Task ID in response does not match expected ID."
            )
        
        # Extract actual content and status
        content = response_data.get("primary_recommendation", response_data.get("summary", json.dumps(response_data)))
        status = response_data.get("status", "success") # Assuming response has a status field
        error_message = response_data.get("error_message")

        return ConsultResponse(
            request_id=response_data.get("task_id"),
            content=content,
            model_name=response_data.get("responder", "Unknown"),
            tokens_used=response_data.get("diagnostics", {}).get("tokens_used", 0),
            latency_ms=(time.time() - start_time) * 1000,
            schema_version=response_data.get("protocol_version", "1.0"),
            status=status,
            error_message=error_message
        )

    async def _is_file_complete(self, filepath: Path) -> bool:
        """Check if file write is complete by verifying stable size."""
        try:
            size1 = filepath.stat().st_size
            await asyncio.sleep(0.1)
            size2 = filepath.stat().st_size
            return size1 == size2 and size1 > 0
        except (OSError, FileNotFoundError):
            return False

    def health_check(self) -> bool:
        """Checks if the communication directories are writable."""
        try:
            test_file = self.requests_dir / "health.check"
            test_file.write_text("ok")
            test_file.unlink()
            return True
        except IOError:
            return False