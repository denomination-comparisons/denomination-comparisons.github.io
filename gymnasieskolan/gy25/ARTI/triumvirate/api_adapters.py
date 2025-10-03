import os
import time
from typing import Dict, Any

from anthropic import AsyncAnthropic, APIStatusError, APIConnectionError, RateLimitError

from .core import ConsultRequest, ConsultResponse, ProviderAdapter


class AnthropicAPIAdapter(ProviderAdapter):
    """Adapter for the Anthropic (Claude) API."""

    def __init__(self, api_key: str = None, default_model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not found. Set the ANTHROPIC_API_KEY environment variable.")
        
        self.client = AsyncAnthropic(api_key=self.api_key)
        self.default_model = default_model

    async def consult(self, req: ConsultRequest) -> ConsultResponse:
        """Sends a request to the Anthropic API and returns the response."""
        start_time = time.time()
        model_to_use = req.model_override or self.default_model
        api_params = req.api_params or {}

        try:
            response = await self.client.messages.create(
                model=model_to_use,
                max_tokens=req.max_tokens,
                system=req.system_prompt if req.system_prompt else None,
                messages=[{"role": "user", "content": req.prompt}],
                **api_params # Pass extra parameters like temperature, top_p, etc.
            )

            content = ""
            if response.content and isinstance(response.content, list):
                text_block = next((block for block in response.content if block.type == 'text'), None)
                if text_block:
                    content = text_block.text

            token_usage = {
                "input": response.usage.input_tokens if response.usage else 0,
                "output": response.usage.output_tokens if response.usage else 0,
            }

            return ConsultResponse(
                request_id=req.request_id,
                response_id=response.id,
                content=content,
                model_name=response.model,
                stop_reason=response.stop_reason,
                token_usage=token_usage,
                latency_ms=(time.time() - start_time) * 1000,
                status="success"
            )

        except (APIStatusError, APIConnectionError, RateLimitError) as e:
            return ConsultResponse(
                request_id=req.request_id,
                model_name=model_to_use,
                latency_ms=(time.time() - start_time) * 1000,
                status="error",
                error_message=f"{type(e).__name__}: {e}"
            )
        except Exception as e:
            return ConsultResponse(
                request_id=req.request_id,
                model_name=model_to_use,
                latency_ms=(time.time() - start_time) * 1000,
                status="error",
                error_message=f"An unexpected error occurred: {e}"
            )

    def health_check(self) -> bool:
        return bool(self.api_key)