import os
import time
import logging
from typing import Any

import anthropic

logger = logging.getLogger(__name__)

_RETRY_DELAYS = [1.0, 2.0, 4.0]


class ClaudeClient:
    """Thin wrapper around the Anthropic SDK with exponential backoff retry."""

    def __init__(self, api_key: str | None = None, default_model: str = "claude-sonnet-4-6"):
        self._client = anthropic.Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])
        self.default_model = default_model

    def message(
        self,
        *,
        system: str,
        user: str,
        model: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> str:
        """Send a single-turn message and return the text content."""
        target_model = model or self.default_model
        last_error: Exception | None = None

        for attempt, delay in enumerate([0.0] + _RETRY_DELAYS):
            if delay:
                logger.warning("Retrying Claude call (attempt %d) after %.0fs", attempt, delay)
                time.sleep(delay)
            try:
                response = self._client.messages.create(
                    model=target_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                )
                if not response.content:
                    return ""
                return response.content[0].text
            except anthropic.RateLimitError as e:
                last_error = e
            except anthropic.APIStatusError as e:
                if e.status_code >= 500:
                    last_error = e
                else:
                    raise

        raise RuntimeError(f"Claude call failed after {len(_RETRY_DELAYS) + 1} attempts") from last_error

    def json_message(self, *, system: str, user: str, model: str | None = None, max_tokens: int = 1024) -> Any:
        """Send a message and parse the response as JSON."""
        import json

        raw = self.message(system=system, user=user, model=model, max_tokens=max_tokens)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Strip markdown code fences if present
            stripped = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(stripped)
