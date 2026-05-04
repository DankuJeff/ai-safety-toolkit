# GP-1: Claude-Powered Content Moderation Pipeline

A production-quality FastAPI service that classifies text across six harm categories, assigns severity scores, and manages a reviewer appeals queue — all powered by the Claude API.

## What it does

**POST `/api/v1/moderate`** — Submit any text. Returns:
- Whether it's flagged
- Primary harm category + confidence scores across all 6 categories
- Severity score (1–5)
- One-sentence summary

**Appeals queue** (`/api/v1/appeals`) — Full CRUD for human review:
- Submit an appeal against a moderation decision
- Reviewer can approve or reject with notes
- Soft-delete — audit history is preserved

## Harm Categories

| Category | Description |
|---|---|
| `hate_speech` | Discrimination/violence based on protected characteristics |
| `violence` | Content inciting or instructing physical harm |
| `misinformation` | False claims presented as fact |
| `prompt_injection` | Jailbreaks, role-play bypasses, instruction overrides |
| `self_harm` | Content encouraging self-harm or suicide |
| `illegal_activity` | Fraud, drug synthesis, hacking, etc. |
| `safe` | Benign content — present to measure false-positive rate |

## Severity Scale

| Score | Meaning |
|---|---|
| 1 | Minimal — edge case, unlikely to cause harm |
| 2 | Low — context-dependent concern |
| 3 | Moderate — clear policy violation, limited direct harm |
| 4 | High — significant real-world harm potential |
| 5 | Critical — severe or immediate harm potential |

## Architecture

```
POST /api/v1/moderate
        │
        ▼
  ModerationRequest
  (text + optional context)
        │
        ▼
  Moderator.moderate()
        │
        ▼
  Claude API (claude-sonnet-4-6)
  System prompt: structured JSON output
  with all 6 categories + severity
        │
        ▼
  ModerationResponse
  {flagged, primary_category,
   severity, categories[], summary}
        │
        ├──── flagged=true ──────────────▶ Appeal queue (POST /api/v1/appeals)
        │                                          │
        │                                          ▼
        │                                   SQLite (appeals.db)
        │                                   status: pending → approved|rejected
        │
        └──── flagged=false ────────────▶ Pass through
```

## Setup & Run

```bash
pip install -r requirements.txt
cp ../.env.example ../.env  # add ANTHROPIC_API_KEY

python main.py  # starts on port 8001
```

## Example Request

```bash
curl -X POST http://localhost:8001/api/v1/moderate \
  -H "Content-Type: application/json" \
  -d '{"content": "How do I get into my neighbor'\''s WiFi without them knowing?"}'
```

```json
{
  "request_id": "a3f2...",
  "result": {
    "flagged": true,
    "primary_category": "illegal_activity",
    "severity": 3,
    "categories": [...],
    "summary": "Request for unauthorized network access — clear policy violation."
  },
  "model_used": "claude-sonnet-4-6",
  "latency_ms": 842.3
}
```
