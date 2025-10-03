import asyncio
import json
import unittest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch
from datetime import datetime # Added
import time # Added
from typing import Any # Added

from triumvirate.orchestrator import TriumvirateOrchestrator
from triumvirate.adapters import FileSystemAdapter
from triumvirate.core import ConsultRequest, ConsultResponse


class TestTriumvirateOrchestrator(unittest.IsolatedAsyncioTestCase):
    """Test suite for the TriumvirateOrchestrator with FileSystemAdapter."""
    
    async def asyncSetUp(self):
        """Create temporary directory for test communications and setup orchestrator."""
        self.test_dir = tempfile.mkdtemp()
        self.communication_dir = Path(self.test_dir) / "triumvirate_communications"
        self.communication_dir.mkdir()

        self.fs_adapter = FileSystemAdapter(communication_dir=str(self.communication_dir))
        self.orchestrator = TriumvirateOrchestrator(
            architect_adapter=self.fs_adapter,
            engineer_adapter=self.fs_adapter, # Using same adapter for simplicity in tests
            default_timeout=1,
            max_retries=1
        )
        self.responses_dir = self.communication_dir / "responses"
    
    async def asyncTearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    async def _wait_for_request_file(self, timeout: float = 2.0) -> str:
        """Wait for a request file to appear and return its task_id."""
        start = time.time()
        requests_dir = self.communication_dir / "requests"
        
        while (time.time() - start) < timeout:
            request_files = list(requests_dir.glob("tcp_request_*.json"))
            if request_files:
                # Assuming only one request file is created per test for simplicity
                with open(request_files[0], 'r', encoding='utf-8') as f:
                    req_content = json.load(f)
                    return req_content["task_id"]
            await asyncio.sleep(0.05)
        
        raise TimeoutError("Request file did not appear within timeout")

    async def _simulate_response(self, request_id: str, content: Dict[str, Any], delay: float = 0.1):
        """Helper to simulate an external agent writing a response file."""
        await asyncio.sleep(delay) # Simulate some processing time
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        response_filename = f"tcp_response_{request_id[:8]}_{timestamp}.json"
        response_path = self.responses_dir / response_filename
        
        # Ensure atomic write for the simulated response
        temp_path = response_path.with_suffix('.tmp')
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2)
        temp_path.replace(response_path)

    async def test_consult_architect_success(self):
        """Test a successful consultation with the architect."""
        prompt = "Design a test system"
        
        # Start the consultation in a background task
        consult_task = asyncio.create_task(self.orchestrator.consult_and_wait(role="architect", prompt=prompt))
        
        # Wait for the request file to appear and get the request_id
        request_id = await self._wait_for_request_file()

        simulated_response_content = {
            "task_id": request_id,
            "protocol_version": "1.0",
            "responder": "Sonnet-4.5",
            "response_type": "planning",
            "summary": "Initial system design complete.",
            "primary_recommendation": "Use microservices architecture.",
            "status": "success",
            "diagnostics": {"tokens_used": 150, "latency_ms": 500}
        }
        await self._simulate_response(request_id, simulated_response_content)
        
        # Await the consultation result
        response = await consult_task
        
        self.assertIsInstance(response, ConsultResponse)
        self.assertEqual(response.request_id, request_id)
        self.assertEqual(response.status, "success")
        self.assertIn("microservices", response.content)
        self.assertEqual(response.model_name, "Sonnet-4.5")
        self.assertGreater(response.tokens_used, 0)
        self.assertGreater(response.latency_ms, 0)

    async def test_consult_architect_timeout(self):
        """Test consultation timeout when no response is received."""
        prompt = "Design a complex system that takes a long time"
        
        # Set a short timeout for this test
        self.orchestrator.default_timeout = 0.5
        self.orchestrator.max_retries = 1

        with self.assertRaises(RuntimeError) as cm:
            await self.orchestrator.consult_and_wait(role="architect", prompt=prompt)
        
        self.assertIn("Consultation failed after 1 attempts", str(cm.exception))
        self.assertIn("Response file not found", str(cm.exception))

    async def test_consult_architect_error_response(self):
        """Test handling of an error response from the architect."""
        prompt = "Request that will cause an error"

        consult_task = asyncio.create_task(self.orchestrator.consult_and_wait(role="architect", prompt=prompt))

        request_id = await self._wait_for_request_file()

        simulated_error_response = {
            "task_id": request_id,
            "protocol_version": "1.0",
            "responder": "Sonnet-4.5",
            "response_type": "error",
            "summary": "Error processing request.",
            "status": "error",
            "error_message": "Insufficient context provided.",
            "diagnostics": {"tokens_used": 50, "latency_ms": 200}
        }
        await self._simulate_response(request_id, simulated_error_response)

        with self.assertRaises(RuntimeError) as cm:
            await consult_task
        
        self.assertIn("Consultation failed", str(cm.exception))
        self.assertIn("Insufficient context provided", str(cm.exception))

    async def test_conversation_history_update(self):
        """Test that conversation history is updated after a successful consultation."""
        prompt = "Initial query for history test"
        consult_task = asyncio.create_task(self.orchestrator.consult_and_wait(role="architect", prompt=prompt))

        request_id = await self._wait_for_request_file()

        simulated_response_content = {
            "task_id": request_id,
            "protocol_version": "1.0",
            "responder": "Sonnet-4.5",
            "response_type": "planning",
            "summary": "History test response.",
            "primary_recommendation": "Log everything.",
            "status": "success",
            "diagnostics": {"tokens_used": 100, "latency_ms": 300}
        }
        await self._simulate_response(request_id, simulated_response_content)

        await consult_task # Wait for the consultation to complete

        history_summary = self.orchestrator.conversation_history.get_summary()
        self.assertIn("History test response.", history_summary)
        self.assertIn("architect", history_summary)

    async def test_generate_api_endpoint_workflow(self):
        """Test the full design-to-code vertical slice workflow."""
        user_request = "Create a /users endpoint that returns a list of users"

        # Use a patch to intercept the consult calls
        async def mock_consult(request: ConsultRequest):
            if request.role == "architect":
                design = {
                    "endpoint": "/users",
                    "method": "GET",
                    "request_model": None,
                    "response_model": "List[User]",
                    "success_criteria": "Returns a 200 OK with a list of user objects."
                }
                return ConsultResponse(
                    request_id=request.request_id,
                    content=json.dumps(design),
                    model_name="mock_architect",
                    tokens_used=100,
                    latency_ms=200,
                    status="success"
                )
            elif request.role == "engineer":
                code = "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/users')\ndef get_users():\n    return [{'id': 1, 'name': 'test'}]"
                return ConsultResponse(
                    request_id=request.request_id,
                    content=code,
                    model_name="mock_engineer",
                    tokens_used=200,
                    latency_ms=300,
                    status="success"
                )
            return ConsultResponse(request_id=request.request_id, content="", model_name="error", tokens_used=0, latency_ms=0, status="error", error_message="Unknown role")

        # We patch the adapter's consult method directly
        with patch.object(self.fs_adapter, 'consult', new=mock_consult):
            result = await self.orchestrator.generate_api_endpoint(user_request)

        self.assertIn("design", result)
        self.assertIn("code", result)
        self.assertEqual(result["design"]["endpoint"], "/users")
        self.assertIn("FastAPI", result["code"])
        self.assertIn("conversation_id", result)



if __name__ == '__main__':
    unittest.main()