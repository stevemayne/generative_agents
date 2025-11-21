# Repository Guidelines

## Project Structure & Module Organization
- `reverie/backend_server/`: Core simulation server. Entry point: `reverie.py`. Agent code lives under `persona/` (cognitive modules, memory structures, prompt templates).
- `environment/frontend_server/`: Django app that renders and replays simulations. Entry point: `manage.py`. Assets under `static_dirs/` and generated data under `storage/` and `compressed_storage/`.
- `reverie/compress_sim_storage.py`: Utility to compress a saved simulation for demos.
- `requirements.txt`: Python dependencies (tested on Python 3.9).

## Build, Test, and Development Commands
- Create venv and install deps:
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -r requirements.txt`
- Run environment (Django) server:
  - `cd environment/frontend_server && python manage.py runserver`
- Run simulation server:
  - `cd reverie/backend_server && python reverie.py`
  - Example in-prompt command: `run 100` (simulates 100 steps)
- Compress a simulation for demo:
  - Edit and run `reverie/compress_sim_storage.py` → call `compress("<simulation-name>")`
- Replay/demo in browser:
  - `http://localhost:8000/replay/<simulation>/<step>/`
  - `http://localhost:8000/demo/<simulation>/<step>/<speed>/`

## Coding Style & Naming Conventions
- Python 3.9; follow PEP 8 (4‑space indents, 88–100 char lines when feasible).
- Names: modules/functions `snake_case`, classes `CapWords`, constants `UPPER_CASE`.
- Keep functions pure where possible; isolate side‑effects (file I/O, HTTP).
- Place agent logic under `reverie/backend_server/persona/` and shared helpers in `reverie/backend_server/global_methods.py`.

## Testing Guidelines
- No formal test harness is bundled. Validate changes by:
  - Running `python manage.py runserver` and exercising replay/demo routes.
  - Running sample simulations via `python reverie.py` and verifying movement/log output.
- If adding tests, prefer `pytest` with files named `test_*.py` near the code under test.

## Commit & Pull Request Guidelines
- Commits: concise, imperative subject (e.g., "fix prompt parsing"), scope in body if needed. Group related changes.
- PRs: include purpose, summary of changes, manual test steps (commands and URLs), and screenshots/GIFs for UI-affecting changes. Link related issues.

## Security & Configuration Tips
- Do not commit secrets. Create `reverie/backend_server/utils.py` locally with your OpenAI API key (this file is git‑ignored). Example keys in README; never hardcode keys elsewhere.
- Generated data under `environment/frontend_server/storage/` can be large; avoid committing outputs unless explicitly required.

