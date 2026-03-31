"""Companion persistence — JSON storage at ~/.config/mini-claude/companion.json

Port of the storage aspects from claude-code-main config.ts (companion field).
Kept separate from the TOML app config because companion data is generated
runtime state, not user configuration.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from .types import CompanionSoul, StoredCompanion

_CONFIG_DIR = Path.home() / ".config" / "mini-claude"
_COMPANION_FILE = _CONFIG_DIR / "companion.json"


def _ensure_dir() -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_stored_companion(path: Path | None = None) -> StoredCompanion | None:
    """Load the stored companion from disk, or None if not hatched yet."""
    fp = path or _COMPANION_FILE
    if not fp.exists():
        return None
    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
        return StoredCompanion(
            name=data["name"],
            personality=data["personality"],
            hatched_at=data["hatchedAt"],
        )
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def save_stored_companion(
    soul: CompanionSoul, path: Path | None = None
) -> StoredCompanion:
    """Save the companion soul to disk and return the stored form."""
    fp = path or _COMPANION_FILE
    fp.parent.mkdir(parents=True, exist_ok=True)

    hatched_at = int(time.time() * 1000)
    data = {
        "name": soul.name,
        "personality": soul.personality,
        "hatchedAt": hatched_at,
    }
    fp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return StoredCompanion(
        name=soul.name,
        personality=soul.personality,
        hatched_at=hatched_at,
    )


def load_companion_muted(path: Path | None = None) -> bool:
    """Check if companion reactions are muted."""
    fp = path or _COMPANION_FILE
    if not fp.exists():
        return False
    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
        return bool(data.get("muted", False))
    except (json.JSONDecodeError, TypeError):
        return False


def save_companion_muted(muted: bool, path: Path | None = None) -> None:
    """Toggle the muted flag in the companion file."""
    fp = path or _COMPANION_FILE
    if not fp.exists():
        return
    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, TypeError):
        return
    data["muted"] = muted
    fp.write_text(json.dumps(data, indent=2), encoding="utf-8")
