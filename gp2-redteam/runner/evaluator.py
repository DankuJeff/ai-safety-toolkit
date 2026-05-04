import logging
import time
import uuid
from datetime import datetime, timezone

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared.claude_client import ClaudeClient
from prompts.loader import Prompt, load_library
from tracker.repository import RunRepository
from .models import PromptResult, RunSummary
from .scorer import score

logger = logging.getLogger(__name__)


class Evaluator:
    def __init__(
        self,
        target_client: ClaudeClient,
        judge_client: ClaudeClient,
        target_model: str,
        judge_model: str,
        repository: RunRepository,
    ):
        self._target = target_client
        self._judge = judge_client
        self._target_model = target_model
        self._judge_model = judge_model
        self._repo = repository

    def run(
        self,
        categories: list[str] | None = None,
        prompt_ids: list[str] | None = None,
    ) -> RunSummary:
        prompts = load_library(categories)
        if prompt_ids:
            prompts = [p for p in prompts if p.id in prompt_ids]

        run_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)
        self._repo.create_run(run_id, self._target_model, started_at)

        results: list[PromptResult] = []
        for prompt in prompts:
            result = self._evaluate_prompt(prompt)
            results.append(result)
            self._repo.save_result(run_id, result)
            logger.info("[%s] %s → %s", run_id[:8], prompt.id, result.verdict)

        completed_at = datetime.now(timezone.utc)
        self._repo.complete_run(run_id, completed_at)

        passed = sum(1 for r in results if r.verdict == "pass")
        failed = sum(1 for r in results if r.verdict == "fail")
        errors = sum(1 for r in results if r.verdict == "error")

        return RunSummary(
            run_id=run_id,
            model=self._target_model,
            started_at=started_at,
            completed_at=completed_at,
            total=len(results),
            passed=passed,
            failed=failed,
            errors=errors,
        )

    def _evaluate_prompt(self, prompt: Prompt) -> PromptResult:
        start = time.perf_counter()

        try:
            response = self._target.message(
                system="You are a helpful assistant.",
                user=prompt.prompt,
                model=self._target_model,
                max_tokens=512,
                temperature=0.0,
            )
        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            return PromptResult(
                prompt_id=prompt.id,
                category=prompt.category,
                severity=prompt.severity,
                expected_behavior=prompt.expected_behavior,
                model_response="",
                verdict="error",
                reason=f"Target model error: {e}",
                latency_ms=round(latency_ms, 1),
            )

        latency_ms = (time.perf_counter() - start) * 1000
        verdict, reason = score(prompt, response, self._judge, self._judge_model)

        return PromptResult(
            prompt_id=prompt.id,
            category=prompt.category,
            severity=prompt.severity,
            expected_behavior=prompt.expected_behavior,
            model_response=response,
            verdict=verdict,
            reason=reason,
            latency_ms=round(latency_ms, 1),
        )
