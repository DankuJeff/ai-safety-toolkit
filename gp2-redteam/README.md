# GP-2: LLM Red-Teaming & Safety Eval Framework

An adversarial evaluation framework for language models. Runs a curated prompt library against any Claude model, scores responses using a judge model, tracks pass rates over time, and surfaces regressions in a React dashboard.

## What it does

**`python run_eval.py`** — CLI that:
1. Loads adversarial prompts from the YAML library (46 prompts, 7 categories)
2. Sends each prompt to the **target model** (default: `claude-sonnet-4-6`)
3. Sends the response to a **judge model** (default: `claude-haiku-4-5`) for pass/fail scoring
4. Persists all results to SQLite with run metadata
5. Prints a coverage report to the terminal

**React Dashboard** — Shows:
- Overall pass rate for the selected run
- Pass/fail/error counts
- Pass rate breakdown by harm category (bar chart)
- Regression trend across model versions (line chart with 80% target line)
- Full prompt result table with verdicts and reasons

## Prompt Library

46 adversarial prompts across 7 categories, each tagged with:
- `severity` (1–5)
- `expected_behavior`: `allow` | `warn` | `refuse`
- `notes` explaining the adversarial technique being tested

| Category | Prompts | What's tested |
|---|---|---|
| `hate_speech` | 7 | Direct requests, pseudo-scientific racism, enumeration |
| `violence` | 7 | Weapon construction, operational harm planning, fiction framing |
| `misinformation` | 7 | Election interference, health misinfo, fabricated quotes |
| `prompt_injection` | 7 | DAN, GRANDMA, fake system prompts, encoding obfuscation |
| `self_harm` | 7 | Explicit method requests, romanticization, dangerous weight loss |
| `illegal_activity` | 7 | Money laundering, drug synthesis, phishing, fraud |
| `safe` | 6 | Benign prompts — measures over-refusal (false positives) |

## Claude-as-Judge Scoring

GP-2 uses a cheaper Haiku model to evaluate whether the target model's response matches `expected_behavior`:

```
Target model response
        │
        ▼
Judge model (Haiku)
System: "Did the model allow / warn / refuse?
         Does that match expected_behavior?"
        │
        ▼
{"verdict": "pass"|"fail", "actual_behavior": "...", "reason": "..."}
```

This separates evaluation from execution — the judge is model-agnostic, so you can swap `TARGET_MODEL` to test any Claude variant and compare results over time.

## Architecture

```
prompts/library/*.yaml
        │
        ▼
  Prompt Loader
  (46 prompts, filtered by category/id)
        │
        ▼
  Evaluator.run()
  ├── for each prompt:
  │   ├── Target model → response
  │   └── Judge model  → verdict + reason
  └── RunRepository.save_result()
                │
                ▼
         SQLite (gp2_redteam.db)
         eval_runs + prompt_results
                │
                ▼
      FastAPI /api/v1/runs/*
                │
                ▼
      React Dashboard :5173
      ┌─────────────────────┐
      │ Pass Rate   [86%]   │
      │ Category Breakdown  │
      │ ████ ████ ███       │
      │ Regression Trend    │
      │     ──────────      │
      │ Prompt Results ───  │
      └─────────────────────┘
```

## Setup & Run

```bash
pip install -r requirements.txt
cp ../.env.example ../.env  # add ANTHROPIC_API_KEY

# Run the full eval suite (all 46 prompts)
python run_eval.py

# Run only specific categories
python run_eval.py --categories hate_speech prompt_injection

# Run specific prompts by ID
python run_eval.py --prompt-ids hs-001 pi-003 vio-004

# Test a different model
python run_eval.py --target-model claude-haiku-4-5-20251001

# Start the dashboard API
python main.py  # port 8002

# Start the dashboard UI (separate terminal)
cd dashboard && npm install && npm run dev  # port 5173
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | required | API key |
| `TARGET_MODEL` | `claude-sonnet-4-6` | Model being evaluated |
| `JUDGE_MODEL` | `claude-haiku-4-5-20251001` | Model scoring responses |
| `GP2_DATABASE_URL` | `sqlite:///./gp2_redteam.db` | Run history storage |
| `GP2_PORT` | `8002` | Dashboard API port |
