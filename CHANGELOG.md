# Changelog

All notable changes to this project will be documented in this format.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-28

### Added
- Initial release of Meridian Retail Support Draft Review Tool
- CLI entry point (`app.py`) with `--case`, `--offline-demo`, `--simulate-timeout` flags
- Policy document (`policy.md`) with rules P1–P4
- Three test cases in `cases.json` (C1, C2, C3)
- Prerecorded outputs in `demo_outputs.json` for offline demos
- Environment setup script (`setup_env.py`) creating `.env` without printing keys
- Template `.env.example` and comprehensive `.gitignore`
- Pinned dependencies in `requirements.txt`
- Full test suite: `test_app.py` (13 tests), `test_setup_env.py` (3 tests)
- Comprehensive `README.md` with architecture, usage, safety guarantees

### Safety Features
- Structured JSON output validation with typed fields
- Failure-safe `UNAVAILABLE` state on any error
- No external side effects (no message sending, refund approval, record changes)
- Offline demo mode for CI/CD without API access
- Timeout simulation for resilience testing

### Architecture
- Grounded generation: model sees only supplied facts + policy
- Human-in-the-loop: every output requires review (`review_status` gates handoff)
- Ollama integration via local HTTP API (`gpt-oss:20b-cloud`)
- Three-section console output: SUPPLIED FACTS, SUPPLIED POLICY, DRAFT RESULT