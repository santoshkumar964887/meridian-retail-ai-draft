# Contributing to Meridian Support Drafter

Thank you for considering a contribution. This project is intentionally minimal —
please keep changes focused and well-tested.

## Getting Started

```bash
git clone <repo-url>
cd meridian-support-drafter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup_env.py
```

## Development Workflow

1. Create a branch: `git checkout -b feature/your-change`
2. Make changes
3. Run tests: `pytest test_app.py test_setup_env.py -v`
4. Run offline demo to verify: `python app.py --case C1 --offline-demo`
5. Commit with a clear message
6. Open a pull request

## Code Standards

- **Python 3.10+** — type hints where practical
- **No external API calls in tests** — use mocks (see existing tests)
- **No new dependencies without justification** — this is a minimal demo
- **Keep CLI output stable** — three-section format must not change
- **Never add features that send messages, approve refunds, or change records**

## Adding a New Case

1. Add entry to `cases.json` with new `case_id` (e.g., `C4`)
2. Add corresponding entry to `demo_outputs.json`
3. Verify: `python app.py --case C4 --offline-demo`
4. Add test coverage in `test_app.py` if logic is new

## Modifying Policy

Edit `policy.md` directly. Changes take effect immediately.
No code changes needed unless policy structure changes.

## Testing Guidelines

- All tests must pass without Ollama running
- Use `unittest.mock` for any external calls
- Test both success and failure paths
- New flags/behaviors need test coverage

## Pull Request Checklist

- [ ] Tests pass (`pytest -v`)
- [ ] Offline demo works for affected cases
- [ ] No secrets or keys committed
- [ ] README updated if user-facing behavior changes
- [ ] CHANGELOG.md updated (see format below)

## Changelog Format

See `CHANGELOG.md` — use the same style:
- `### Added` for new features
- `### Changed` for modifications
- `### Fixed` for bug fixes
- `### Removed` for deletions

## Questions?

Open an issue for discussion before large changes.