# AI Safety Toolkit

A production-quality monorepo containing two safety systems built on the Claude API, targeting the content integrity and safety evaluation gaps common in frontier AI deployments.

**Built as gap-closing portfolio work toward OpenAI TPM, Safety Systems Engineering.**

---

## Projects

### GP-1 — Claude-Powered Content Moderation Pipeline
[`gp1-moderation/`](./gp1-moderation/)

A FastAPI service that classifies text across six harm categories, assigns severity scores (1–5), and manages an appeals review queue with full CRUD.

- **Harm categories:** hate speech, violence, misinformation, prompt injection, self-harm, illegal activity
- **Severity scoring:** 1 (borderline) → 5 (critical / immediate real-world harm)
- **Appeals queue:** SQLite-backed, soft-delete, reviewer note support
- **Stack:** Python 3.11, FastAPI, Claude API, SQLAlchemy, Pydantic v2

### GP-2 — LLM Red-Teaming & Safety Eval Framework
[`gp2-redteam/`](./gp2-redteam/)

An adversarial evaluation framework that runs a curated prompt library against any Claude model, scores responses using a judge model, tracks pass rates over time, and surfaces regressions in a React dashboard.

- **Prompt library:** 46 adversarial prompts across 7 categories, tagged by severity and expected behavior
- **Claude-as-judge scoring:** cheaper Haiku model evaluates target model responses for pass/fail
- **Regression tracking:** SQLite run history, per-category pass rates, model-version comparisons
- **Dashboard:** React + Recharts — coverage report, category breakdown, regression trend chart
- **Stack:** Python 3.11, FastAPI, Claude API, SQLAlchemy, React 18, Vite, Tailwind, Recharts

---

## Shared Infrastructure

[`shared/`](./shared/) — common harm taxonomy (enums + definitions) and a Claude API client wrapper with exponential backoff retry (3 attempts: 1s / 2s / 4s delays).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Claude API                           │
│           (claude-sonnet-4-6 / claude-haiku-4-5)           │
└───────────────────┬──────────────────┬──────────────────────┘
                    │                  │
        ┌───────────▼──────┐  ┌────────▼───────────────┐
        │   GP-1           │  │   GP-2                 │
        │   Moderation     │  │   Red-Teaming Eval     │
        │   Pipeline       │  │   Framework            │
        │                  │  │                        │
        │ ┌──────────────┐ │  │ ┌──────────────────┐  │
        │ │ Harm         │ │  │ │ Prompt Library   │  │
        │ │ Classifier   │ │  │ │ (46 adversarial  │  │
        │ │              │ │  │ │  prompts / YAML) │  │
        │ │ Severity 1-5 │ │  │ └────────┬─────────┘  │
        │ └──────┬───────┘ │  │          │             │
        │        │         │  │ ┌────────▼─────────┐  │
        │ ┌──────▼───────┐ │  │ │ Eval Runner +    │  │
        │ │ Appeals      │ │  │ │ Claude-as-Judge   │  │
        │ │ Review Queue │ │  │ │ Scorer           │  │
        │ │ (SQLite)     │ │  │ └────────┬─────────┘  │
        │ └──────────────┘ │  │          │             │
        │                  │  │ ┌────────▼─────────┐  │
        │  REST API :8001  │  │ │ Run Tracker      │  │
        └──────────────────┘  │ │ (SQLite)         │  │
                              │ └────────┬─────────┘  │
                              │          │             │
                              │ ┌────────▼─────────┐  │
                              │ │ React Dashboard  │  │
                              │ │ :5173 / :8002    │  │
                              │ └──────────────────┘  │
                              └────────────────────────┘
```

---

## Setup

```bash
# Copy environment template
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# Install Python deps (per service)
cd gp1-moderation && pip install -r requirements.txt
cd ../gp2-redteam && pip install -r requirements.txt

# Install dashboard deps
cd gp2-redteam/dashboard && npm install
```

## Running

```bash
# GP-1: Moderation API (port 8001)
cd gp1-moderation && python main.py

# GP-2: Run an eval suite
cd gp2-redteam && python run_eval.py

# GP-2: Dashboard API + UI (port 8002 / 5173)
cd gp2-redteam && python main.py          # API
cd gp2-redteam/dashboard && npm run dev   # Dev UI
```

---

## Key Design Decisions

**Claude-as-judge scoring** — GP-2 uses a cheaper Haiku model to evaluate whether the target model's response matches the expected behavior (allow / warn / refuse). This separates the evaluation concern from the target model, enabling model-agnostic regression testing.

**Shared harm taxonomy** — `HarmCategory` and `Severity` enums are defined once in `shared/` and imported by both services, ensuring consistent category definitions across classification and evaluation.

**Soft deletes** — All appeal records use `deleted_at timestamptz` rather than hard deletes, preserving audit history.

**Adversarial prompt design** — Each prompt is tagged with `expected_behavior` (allow / warn / refuse) and `severity` (1–5). Safe-category prompts are included specifically to measure false-positive rates — over-refusal is treated as a failure, not a safe default.
