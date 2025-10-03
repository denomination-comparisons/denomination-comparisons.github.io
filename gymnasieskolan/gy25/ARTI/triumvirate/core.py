from typing import Protocol, Dict, Any, List, Optional
from dataclasses import dataclass, field
import uuid
from datetime import datetime


@dataclass
class ConsultRequest:
    """Data class for a consultation request, now with more detailed fields."""
    request_id: str
    conversation_id: str
    role: str
    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: int = 4096
    timeout: float = 120.0
    schema_version: str = "2.0" # Upgrading to new version
    
    # Optional overrides and parameters
    model_override: Optional[str] = None
    api_params: Optional[Dict[str, Any]] = None # For temperature, top_p, etc.

    # Original TCP fields for context
    request_type: str = "planning"
    priority: str = "medium"
    urgency: str = "normal"
    context: Optional[Dict[str, Any]] = None
    requirements: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None
    success_criteria: Optional[Dict[str, Any]] = None
    specific_questions: Optional[List[str]] = None
    expected_response_format: Optional[Dict[str, Any]] = None


@dataclass
class ConsultResponse:
    """Data class for a consultation response, now with more detailed metadata."""
    request_id: str
    response_id: Optional[str] = None # The ID of the response from the API provider
    content: str = ""
    model_name: str = ""
    stop_reason: Optional[str] = None
    token_usage: Dict[str, int] = field(default_factory=dict) # e.g., {"input": 100, "output": 250}
    latency_ms: float = 0.0
    schema_version: str = "2.0"
    status: str = "success"
    error_message: Optional[str] = None


class ProviderAdapter(Protocol):
    """Protocol for a provider adapter that can send requests and receive responses."""
    async def consult(self, req: ConsultRequest) -> ConsultResponse:
        """
        Performs a full consultation, sending a request and returning a response.
        """
        ...

    def health_check(self) -> bool:
        """Checks if the provider is available."""
        ...

class ConversationHistory:
    """Manages conversation history and context for the orchestrator."""
    
    def __init__(self, max_history_entries: int = 100):
        self.history: List[Dict] = []
        self.max_history_entries = max_history_entries
        self.conversation_id = str(uuid.uuid4())
    
    def add_entry(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.history.append(entry)
        if len(self.history) > self.max_history_entries:
            self.history = self.history[-self.max_history_entries:]
    
    def get_summary(self, max_entries: int = 5, max_content_length: int = 200) -> str:
        if not self.history:
            return "No previous discussion."
        recent = self.history[-max_entries:]
        summary_parts = []
        for entry in recent:
            truncated_content = entry['content']
            if len(truncated_content) > max_content_length:
                truncated_content = truncated_content[:max_content_length] + '...'
            summary_parts.append(f"{entry['role']}: {truncated_content}")
        return "\n".join(summary_parts)

    def get_conversation_id(self) -> str:
        return self.conversation_id
