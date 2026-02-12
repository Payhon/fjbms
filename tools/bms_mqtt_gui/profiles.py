from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ProfileError(Exception):
    pass


@dataclass(frozen=True)
class DeviceProfile:
    id: str
    name: str
    description: str
    raw: dict[str, Any]


def list_profile_files(profile_dir: str | Path) -> list[Path]:
    p = Path(profile_dir)
    if not p.exists() or not p.is_dir():
        return []
    return sorted([x for x in p.glob("*.json") if x.is_file()])


def load_profile(path: str | Path) -> DeviceProfile:
    p = Path(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise ProfileError(f"failed to parse json: {p}: {e}") from e

    if not isinstance(data, dict):
        raise ProfileError(f"profile must be a json object: {p}")
    pid = str(data.get("id") or p.stem)
    name = str(data.get("name") or pid)
    desc = str(data.get("description") or "")
    return DeviceProfile(id=pid, name=name, description=desc, raw=data)


def load_profiles(profile_dir: str | Path) -> list[DeviceProfile]:
    out: list[DeviceProfile] = []
    for f in list_profile_files(profile_dir):
        try:
            out.append(load_profile(f))
        except Exception:
            # ignore broken profile files
            continue
    return out

