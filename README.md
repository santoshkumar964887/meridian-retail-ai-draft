# Meridian Retail Support Draft Review Tool

A minimal, production-aware CLI tool that assists human support agents by drafting
responses to customer cases using only supplied facts and a local policy document.
The tool never sends messages, approves refunds, or changes records — it only
produces a structured draft for human review.

---

## Purpose

This tool demonstrates a safe, auditable pattern for AI-assisted customer support:
- **Grounded generation**: Model sees only the case facts and policy — no external knowledge
- **Structured output**: Enforced JSON schema with typed fields
- **Human-in-the-loop**: Every output requires review before use
- **Failure-safe**: Any error returns a clear `UNAVAILABLE` state, never a stale draft
- **Testable offline**: `--offline-demo` and `--simulate-timeout` flags enable CI/CD without API access

---

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐
│  cases.json │────▶│             │     │                  │
└─────────────┘     │   app.py    │────▶│  Ollama API      │
                    │  (CLI)      │     │  (gpt-oss:20b-   │
┌─────────────┐     │             │     │   cloud)         │
│ policy.md   │────▶│             │     │                  │
└─────────────┘     └──────┬──────┘     └────────┬─────────┘
                           │                     │
                    ┌──────▼──────┐     ┌────────▼─────────┐
                    │  Validate   │     │  Structured JSON │
                    │  Response   │     │  Response        │
                    └──────┬──────┘     └────────┬─────────┘
                           │                     │
                    ┌──────▼─────────────────────▼──────┐
                    │   Three-section console output    │
                    │  1. SUPPLIED FACTS                │
                    │  2. SUPPLIED POLICY               │
                    │  3. DRAFT RESULT FOR HUMAN REVIEW │
                    └───────────────────────────────────┘
```

---

## Quick Start

### 1. Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Model

```bash
python setup_env.py
# Enter model name when prompted (default: gpt-oss:20b-cloud)
```

This creates a local `.env` file (gitignored) with `OLLAMA_MODEL=your-model`.

### 3. Start Ollama (separate terminal)

```bash
ollama serve
ollama pull gpt-oss:20b-cloud
```

### 4. Run the Tool

```bash
# Basic usage - requires running Ollama
python app.py --case C1

# Offline demo - no Ollama needed, uses demo_outputs.json
python app.py --case C1 --offline-demo

# Simulate timeout - tests failure handling
python app.py --case C1 --simulate-timeout
```

---

## Detailed Usage

### Command Line Arguments

| Argument | Required | Values | Description |
|----------|----------|--------|-------------|
| `--case` | Yes | `C1`, `C2`, `C3` | Selects the support case to process |
| `--offline-demo` | No | flag | Loads prerecorded output from `demo_outputs.json`, prints "No model API was called" |
| `--simulate-timeout` | No | flag | Skips API call, returns `UNAVAILABLE` status with fallback message |

### Case Details

| Case | Product | Issue | Delivery Date | Status | Expected Behavior |
|------|---------|-------|---------------|--------|-------------------|
| **C1** | Jacket | Zip broken on arrival | 2026-09-15 (yesterday) | open | `READY_FOR_HUMAN_REVIEW` — within 2-day window (P1, P2) |
| **C2** | Jacket | Zip broken | `null` (missing) | open | `NEEDS_INFORMATION` — needs delivery date (P2) |
| **C3** | Shoes | Confirm resolution | 2026-09-10 | open | `BLOCKED` — issue still open, cannot confirm resolved (P3) |

### Output Format

The tool always prints three clearly labeled sections:

```
============================================================
SUPPLIED FACTS
============================================================
{ ... case JSON ... }

============================================================
SUPPLIED POLICY
============================================================
# Meridian Retail Support Drafting Policy
P1. Damage reported within two days...

============================================================
DRAFT RESULT FOR HUMAN REVIEW
============================================================
[No model API was called]          ← only with --offline-demo
draft_reply: "Thank you for..."
evidence_refs: ["P1", "P2"]
missing_information: []
review_status: READY_FOR_HUMAN_REVIEW
```

### Response Schema

The model must return JSON with exactly these fields:

| Field | Type | Description |
|-------|------|-------------|
| `draft_reply` | string | Plain-text response for the customer |
| `evidence_refs` | array[string] | Policy IDs cited (e.g., `["P1", "P2"]`) |
| `missing_information` | array[string] | Field names needed from user |
| `review_status` | enum | `READY_FOR_HUMAN_REVIEW` \| `NEEDS_INFORMATION` \| `BLOCKED` |

**Validation**: The tool validates structure and types before display. Invalid or missing responses → `UNAVAILABLE` state.

---

## Policy Reference (`policy.md`)

| ID | Rule |
|----|------|
| **P1** | Damage reported within 2 days of delivery → refer for human return review (not auto-approved) |
| **P2** | Delivery date required for 2-day rule; if missing, ask for it |
| **P3** | If issue status is `open`, draft must NOT say issue is resolved |
| **P4** | Assistant drafts for human review ONLY; cannot approve refunds, send messages, or change records |

---

## Configuration

### `.env` (created by `setup_env.py`, gitignored)

```bash
OLLAMA_MODEL=gpt-oss:20b-cloud
```

### `.env.example` (committed template)

```bash
OLLAMA_MODEL=your-model-name
```

### Model Requirements

- Must support JSON mode / structured output
- Recommended: `gpt-oss:20b-cloud` via Ollama
- Endpoint: `http://localhost:11434/api/generate`

---

## Files in This Project

| File | Purpose |
|------|---------|
| `app.py` | Main CLI entry point |
| `policy.md` | Support drafting policy (P1-P4) |
| `cases.json` | Three test cases (C1, C2, C3) |
| `demo_outputs.json` | Prerecorded model outputs for offline demo |
| `setup_env.py` | Interactive `.env` creator (never prints key) |
| `.env.example` | Template for environment config |
| `.gitignore` | Excludes `.env`, `.venv`, `__pycache__`, `.pytest_cache` |
| `requirements.txt` | Pinned dependencies |
| `test_app.py` | Unit tests for app logic (no external API) |
| `test_setup_env.py` | Unit tests for env setup |
| `README.md` | This file |

---

## Testing

All tests run without external API calls using mocked responses:

```bash
# Run all tests
pytest test_app.py test_setup_env.py -v

# Run with coverage
pytest --cov=app --cov=setup_env test_app.py test_setup_env.py
```

### Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| `app.py` | 13 | Case loading, policy loading, prompt building, response validation, unavailable states, offline demo, timeout simulation, Ollama success/failure mocking |
| `setup_env.py` | 3 | Writes key, uses default model, never prints key to stdout |

---

## Safety Guarantees

| Guarantee | Implementation |
|-----------|----------------|
| **No external actions** | Tool only prints to stdout; no HTTP calls except to Ollama |
| **No refund approval** | Policy P4 enforced in prompt; output schema has no "approve" field |
| **No message sending** | Output is a draft only; `review_status` gates human handoff |
| **No record changes** | Read-only access to `cases.json` and `policy.md` |
| **Failure transparency** | Any error → `review_status: UNAVAILABLE` with fallback reason |
| **No key leakage** | `setup_env.py` writes `.env` but never prints the value |

---

## Extending the Tool

### Add a New Case

1. Add entry to `cases.json` with new `case_id` (e.g., `C4`)
2. Add corresponding entry to `demo_outputs.json`
3. Run `python app.py --case C4 --offline-demo` to verify

### Modify Policy

Edit `policy.md` — changes take effect immediately on next run.

### Change Model

```bash
python setup_env.py
# Enter new model name
```

Or edit `.env` directly.

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| `ModuleNotFoundError` | Activate venv: `source .venv/bin/activate` |
| `Connection refused` | Start Ollama: `ollama serve` |
| `Model not found` | Pull model: `ollama pull gpt-oss:20b-cloud` |
| `Invalid model response` | Check model supports JSON output; try `--offline-demo` |
| `Permission denied` | Ensure `.venv/bin/python` is executable |

---

## License

Internal demo — Meridian Retail classroom use only.