# Architecture Guide

High-level map of the simulation stack: a Python backend that runs the agents
and writes state to disk, plus a Django/Phaser frontend that visualizes and
drives the step loop.

## Repository Layout (entry points)
- Backend simulation server: `reverie/backend_server/reverie.py` (run with
  `python reverie.py`). Core classes live alongside it (`maze.py`,
  `path_finder.py`, and the `persona/` package).
- Frontend web server: `environment/frontend_server/manage.py` (Django). Views
  are in `environment/frontend_server/translator/views.py`; Phaser UI lives in
  `templates/home/`.
- Shared helpers: `reverie/backend_server/global_methods.py` and
  `environment/frontend_server/global_methods.py` (basic file/fs utilities and
  helpers).
- Storage contract: `environment/frontend_server/storage/<sim_code>/` contains
  the evolving simulation assets (environment snapshots, movements, persona
  bootstrap memory), and `temp_storage/` is used for signaling the active
  simulation and step.
- Demo bundling: `reverie/compress_sim_storage.py` compresses a finished run
  into `environment/frontend_server/compressed_storage/` for replay without
  the live backend.

## Backend Responsibilities (`reverie/backend_server`)
- `ReverieServer` in `reverie.py` is the long-running backend process. It:
  - Forks an existing simulation folder into a new run (copies assets and
    rewrites `reverie/meta.json`).
  - Loads global state (clock, maze, persona roster, current step).
  - Maintains persona instances and their tile positions inside a `Maze`.
  - Drives the step loop via `start_server(int_counter)`, consuming frontend
    environment files and emitting movement files.
  - Offers an interactive REPL (`open_server`) for running steps, saving, and
    inspecting persona state.
- Persona pipeline (`persona/persona.py`):
  - Each `Persona` holds spatial memory, associative memory, and scratch
    (short-term) state loaded from `bootstrap_memory/`.
  - `move()` wires the cognition chain: `perceive` -> `retrieve` -> `plan` ->
    `reflect` -> `execute`, returning the next tile, chat balloon, and action
    description.
- Maze and movement:
  - `maze.py` loads the tile map (objects, sectors/arenas, events) and allows
    querying/marking events on tiles.
  - `path_finder.py` handles grid navigation for movement planning.
- Filesystem constants (paths to assets, storage, temp storage) are defined in
  `reverie/backend_server/utils.py` and `global_methods.py`, so backend always
  reads/writes under `environment/frontend_server/`.

## Frontend Responsibilities (`environment/frontend_server`)
- Django endpoints (`translator/views.py`):
  - `landing` and `home`: HTML shells; `home` picks up the active simulation
    from `temp_storage/curr_sim_code.json` and seeds Phaser with persona spawn
    positions.
  - `process_environment`: POST endpoint that writes the current environment
    snapshot from the browser to `storage/<sim_code>/environment/<step>.json`.
  - `update_environment`: POST endpoint that polls for backend-produced moves
    from `storage/<sim_code>/movement/<step>.json` and returns them as JSON.
  - `demo` / `replay`: render precomputed runs (from `compressed_storage/` or
    `storage/`) and skip live backend communication.
  - `replay_persona_state`: renders persisted persona memory snapshots for a
    given step/persona.
  - `path_tester` endpoints support a spatial memory capture mode.
- Client engine (`templates/home/main_script.html`):
  - Phaser scene renders the tile map and persona sprites.
  - Orchestrates three phases per frame: `process` (send positions) ->
    `update` (poll backend for moves) -> `execute` (animate movement and UI
    labels). Advances the step counter after execution completes.
  - Displays meta clock, persona actions, target addresses, and chat balloons.

## Single-Step Flow (live simulation)
1) Backend waits: `ReverieServer.start_server` watches
   `storage/<sim_code>/environment/<step>.json` for the current step.
2) Frontend `process` phase: Phaser reads persona positions, builds an
   environment JSON with `{persona: {x, y, maze}}`, and POSTs it to
   `/process_environment/`, which writes the file the backend is watching.
3) Backend tick: when the environment file appears, `start_server` loads it,
   aligns internal persona tiles, asks each persona to `move(...)`, and writes
   `movement/<step>.json` containing the per-persona next tile, pronunciatio
   emoji/text, description, chat snippets, plus `meta.curr_time`. It advances
   the simulation clock and step.
4) Frontend `update` phase: browser polls `/update_environment/` until it sees
   `movement/<step>.json`, then enters `execute`.
5) Frontend `execute` phase: animates each persona toward the target tile,
   updates on-screen action/location/chat, advances its own step counter, and
   loops back to `process` for the next tick.

## Running the system (typical flow)
- Start backend: `cd reverie/backend_server && python reverie.py`, enter the
  fork origin and new sim codes, then use the REPL (e.g., `run 100`) to step.
- Start frontend: `cd environment/frontend_server && python manage.py runserver`
  and open the home URL; it auto-loads the active sim declared in
  `temp_storage/`.
- Replay/demo without backend: use `/replay/<sim>/<step>/` or
  `/demo/<sim>/<step>/<speed>/` to stream stored movement files.

## Where data lives
- `storage/<sim_code>/environment/<n>.json`: persona positions after the
  frontend executes step `n`.
- `storage/<sim_code>/movement/<n>.json`: backend-computed moves the frontend
  should execute for step `n`.
- `storage/<sim_code>/personas/<name>/bootstrap_memory/`: persisted persona
  memories (spatial, associative, scratch).
- `temp_storage/curr_sim_code.json` and `temp_storage/curr_step.json`: simple
  coordination files telling the frontend which simulation and step to load at
  startup.

## How this maps to the paper (arXiv:2304.03442)
- Core loop: the paper’s perceive → retrieve → plan → reflect → act chain is
  implemented by `Persona.move()` calling cognitive modules under
  `persona/cognitive_modules/`.
- Memory stream: long-term records live in associative memory
  (`memory_structures/associative_memory.py`), spatial context in
  `spatial_memory.py`, and short-term/schedule state in `scratch.py`. These are
  persisted under each persona’s `bootstrap_memory/`.
- Retrieval: the paper’s relevance/recency/importance scoring is encapsulated
  inside the retrieve module; the backend passes current perceptions from the
  `Maze` to drive that scoring.
- Reflection: `reflect()` synthesizes higher-level inferences and writes them
  back into the associative memory stream, mirroring the paper’s recursive
  reflections.
- Planning: long- and short-term plans (daily schedule decomposition, target
  addresses) are produced in the `plan` module, stored in scratch, then turned
  into executable tile targets by `execute`.
- Social behaviors: conversation content and chat buffers in scratch allow
  personas to diffuse facts and coordinate (e.g., party invitations) as
  described in the paper’s Valentine’s Day example; frontend displays these via
  the `chat` payload in movement files.
