import hashlib
import json
import logging
import sys
import os
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.claude_client import ClaudeClient
from shared.taxonomy import HARM_DEFINITIONS, HarmCategory, Severity
from .models import CategoryResult, ModerationRequest, ModerationResponse, ModerationResult

logger = logging.getLogger(__name__)

_CATEGORY_LIST = "\n".join(
    f"- {cat.value}: {defn}" for cat, defn in HARM_DEFINITIONS.items()
)

_SYSTEM_PROMPT = f"""You are a content moderation classifier. Analyze the provided text and return a JSON object with this exact structure:

{{
  "flagged": true | false,
  "primary_category": "<category>",
  "severity": <1-5>,
  "categories": [
    {{
      "category": "<category>",
      "confidence": <0.0-1.0>,
      "explanation": "<one sentence>"
    }}
  ],
  "summary": "<one sentence overall assessment>"
}}

Harm categories:
{_CATEGORY_LIST}

Severity scale:
1 = minimal / borderline
2 = low / context-dependent
3 = moderate / clear policy violation
4 = high / significant real-world harm potential
5 = critical / severe or immediate harm

Rules:
- Include ALL categories in the response, even those with confidence 0.0
- Set flagged=true if any category (except "safe") has confidence >= 0.5
- primary_category must be the highest-confidence harmful category, or "safe" if none
- Return ONLY the JSON object — no markdown, no commentary
"""


class Moderator:
    def __init__(self, client: ClaudeClient):
        self._client = client

    def moderate(self, request: ModerationRequest) -> ModerationResponse:
        start = time.perf_counter()
        request_id = str(uuid.uuid4())
        content_hash = hashlib.sha256(request.content.encode()).hexdigest()[:16]

        user_prompt = f"Content to moderate:\n\n{request.content}"
        if request.context:
            user_prompt = f"Context: {request.context}\n\n{user_prompt}"

        raw = self._client.message(system=_SYSTEM_PROMPT, user=user_prompt, max_tokens=800)
        latency_ms = (time.perf_counter() - start) * 1000

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            stripped = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            data = json.loads(stripped)

        categories = [
            CategoryResult(
                category=HarmCategory(c["category"]),
                confidence=float(c["confidence"]),
                explanation=c["explanation"],
            )
            for c in data["categories"]
        ]

        result = ModerationResult(
            flagged=bool(data["flagged"]),
            primary_category=HarmCategory(data["primary_category"]),
            severity=Severity(int(data["severity"])),
            categories=categories,
            summary=data["summary"],
            content_hash=content_hash,
        )

        logger.info(
            "moderation request_id=%s flagged=%s category=%s severity=%d latency=%.0fms",
            request_id, result.flagged, result.primary_category, result.severity, latency_ms,
        )

        return ModerationResponse(
            request_id=request_id,
            result=result,
            model_used=self._client.default_model,
            latency_ms=round(latency_ms, 1),
        )
