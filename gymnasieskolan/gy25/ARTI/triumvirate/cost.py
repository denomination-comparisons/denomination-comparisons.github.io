from typing import Dict

# Prices per million tokens (input/output)
MODEL_PRICING = {
    "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
    "mock_architect": {"input": 0.0, "output": 0.0},
    "mock_engineer": {"input": 0.0, "output": 0.0},
    "default": {"input": 1.00, "output": 1.00}, 
}

class CostTracker:
    """Tracks the cumulative cost of consultations for each conversation."""
    def __init__(self):
        self.conversation_costs: Dict[str, float] = {}

    def record_consultation(self, conversation_id: str, token_usage: Dict[str, int], model_name: str) -> None:
        """Records the cost of a single consultation and adds it to the conversation's total."""
        cost = self._calculate_cost(token_usage, model_name)
        current_cost = self.conversation_costs.get(conversation_id, 0.0)
        self.conversation_costs[conversation_id] = current_cost + cost

    def _calculate_cost(self, token_usage: Dict[str, int], model: str) -> float:
        """Calculates the cost based on token count and model pricing."""
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
        input_cost = (token_usage.get("input", 0) / 1_000_000) * pricing.get("input", 0.0)
        output_cost = (token_usage.get("output", 0) / 1_000_000) * pricing.get("output", 0.0)
        return input_cost + output_cost

    def get_conversation_cost(self, conversation_id: str) -> float:
        """Returns the total cost for a given conversation."""
        return self.conversation_costs.get(conversation_id, 0.0)