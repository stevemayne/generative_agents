"""
Shared IPC facade between the simulation backend and any frontend runner.
Encapsulates the file-based contract (environment/<step>.json, movement/<step>.json)
and derives storage locations relative to the repository root so both backend
and frontend can use it without hardcoded paths.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
STORAGE_ROOT = REPO_ROOT / "environment" / "frontend_server" / "storage"
TEMP_STORAGE_ROOT = REPO_ROOT / "environment" / "frontend_server" / "temp_storage"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open() as handle:
            return json.load(handle)
    except FileNotFoundError:
        return None
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to read %s: %s", path, exc)
        return None


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_parent(path)
    with path.open("w") as handle:
        handle.write(json.dumps(payload, indent=2))


class FrontendInterface:
    """
    Handles file-based communication between the backend and a frontend game
    loop. This wraps the write/read logic currently implemented via Django
    endpoints so alternate clients can reuse it directly.
    """

    def __init__(self, sim_code: str, storage_root: Path = STORAGE_ROOT) -> None:
        self.sim_code = sim_code
        self.storage_root = Path(storage_root)

    def _env_path(self, step: int) -> Path:
        return self.storage_root / self.sim_code / "environment" / f"{step}.json"

    def _move_path(self, step: int) -> Path:
        return self.storage_root / self.sim_code / "movement" / f"{step}.json"

    def write_environment(self, step: int, environment: Dict[str, Any]) -> None:
        """Persist the current world state for a step so the backend can consume it."""
        _write_json(self._env_path(step), environment)

    def read_environment(self, step: int) -> Optional[Dict[str, Any]]:
        """Load the environment snapshot for a step if present."""
        return _read_json(self._env_path(step))

    def wait_for_environment(
        self, step: int, timeout_s: float = 10.0, poll_interval_s: float = 0.1
    ) -> Optional[Dict[str, Any]]:
        """Poll for an environment snapshot until it appears or timeout."""
        start = time.time()
        while time.time() - start < timeout_s:
            env = self.read_environment(step)
            if env is not None:
                return env
            time.sleep(poll_interval_s)
        return None

    def write_movement(self, step: int, movement: Dict[str, Any]) -> None:
        """Persist backend-produced movement for a step."""
        _write_json(self._move_path(step), movement)

    def read_movement(self, step: int) -> Optional[Dict[str, Any]]:
        """Read the backend-produced movement for a step if it exists."""
        return _read_json(self._move_path(step))

    def wait_for_movement(
        self, step: int, timeout_s: float = 10.0, poll_interval_s: float = 0.1
    ) -> Optional[Dict[str, Any]]:
        """Poll for movement for a given step until it arrives or timeout."""
        start = time.time()
        while time.time() - start < timeout_s:
            movement = self.read_movement(step)
            if movement is not None:
                return movement
            time.sleep(poll_interval_s)
        return None


def current_sim_paths() -> Dict[str, Path]:
    """
    Convenience for temp files that coordinate the active simulation.
    """
    return {
        "curr_sim": TEMP_STORAGE_ROOT / "curr_sim_code.json",
        "curr_step": TEMP_STORAGE_ROOT / "curr_step.json",
    }
