import json
import unittest
import tempfile
import shutil
import time
from pathlib import Path
from datetime import datetime
from _consult_architect_implementation import TriumvirateOrchestrator, ConversationHistory


class TestReceiveArchitectResponse(unittest.TestCase):
    """Test suite for _receive_architect_response method."""
    
    def setUp(self):
        """Create temporary directory and orchestrator."""
        self.test_dir = tempfile.mkdtemp()
        self.orchestrator = TriumvirateOrchestrator(
            project_summary="Test project",
            communication_dir=self.test_dir
        )
        self.task_id = "12345678-1234-1234-1234-123456789abc"
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)
    
    def _create_mock_response_file(self, task_id: str, response_data: dict) -> Path:
        """Helper to create a mock response file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"tcp_response_{task_id[:8]}_{timestamp}.json"
        filepath = self.orchestrator.responses_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2)
        
        return filepath
    
    def test_successful_response_receipt(self):
        """Test successful receipt and parsing of valid response."""
        response_data = {
            "task_id": self.task_id,
            "protocol_version": "1.0",
            "response_type": "plan",
            "summary": "Test summary",
            "primary_recommendation": {"approach": "Test approach", "rationale": "Test rationale", "implementation_steps": []},
            "validation_steps": [],
            "next_actions": []
        }
        self._create_mock_response_file(self.task_id, response_data)
        
        result = self.orchestrator._receive_architect_response(self.task_id)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['response_type'], 'plan')
        self.assertEqual(result['summary'], 'Test summary')
        self.assertTrue(result['has_artifacts'] is False)
        self.assertEqual(result['response_data']['task_id'], self.task_id)
    
    def test_file_not_found(self):
        """Test error handling when response file is not found."""
        result = self.orchestrator._receive_architect_response(self.task_id)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error_type'], 'file_not_found')
    
    def test_malformed_json(self):
        """Test error handling for malformed JSON."""
        filepath = self.orchestrator.responses_dir / f"tcp_response_{self.task_id[:8]}_test.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('{"key": "value",}')  # Malformed JSON with trailing comma
        
        result = self.orchestrator._receive_architect_response(self.task_id)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error_type'], 'json_parse_error')
    
    def test_validation_error(self):
        """Test error handling for response that fails validation."""
        response_data = {
            "task_id": "wrong-id"  # Mismatched task_id
        }
        self._create_mock_response_file(self.task_id, response_data)
        
        result = self.orchestrator._receive_architect_response(self.task_id)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error_type'], 'validation_error')
    
    def test_timeout_functionality(self):
        """Test timeout functionality when file doesn't appear."""
        start_time = time.time()
        result = self.orchestrator._receive_architect_response(self.task_id, timeout_seconds=1)
        end_time = time.time()
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error_type'], 'timeout_error')
        self.assertGreaterEqual(end_time - start_time, 1.0)

    def test_artifact_handling(self):
        """Test that artifacts are correctly extracted and stored."""
        response_data = {
            "task_id": self.task_id,
            "protocol_version": "1.0",
            "response_type": "plan",
            "summary": "Test summary",
            "primary_recommendation": {"approach": "Test approach", "rationale": "Test rationale", "implementation_steps": []},
            "validation_steps": [],
            "next_actions": [],
            "artifacts": [
                {"type": "python_code", "name": "test.py", "content": "print('hello')"}
            ]
        }
        self._create_mock_response_file(self.task_id, response_data)
        
        result = self.orchestrator._receive_architect_response(self.task_id)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['has_artifacts'])
        self.assertIn(self.task_id, self.orchestrator.artifacts)
        self.assertEqual(len(self.orchestrator.artifacts[self.task_id]), 1)
        self.assertEqual(self.orchestrator.artifacts[self.task_id][0]['name'], 'test.py')

if __name__ == '__main__':
    unittest.main()
