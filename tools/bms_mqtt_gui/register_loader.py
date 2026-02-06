from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


def _parse_hex_maybe(s: str) -> int | None:
    t = s.strip()
    if not t:
        return None
    if t.startswith(("0x", "0X")):
        try:
            return int(t, 16)
        except Exception:
            return None
    # Accept bare hex like "11A" within the address table.
    if re.fullmatch(r"[0-9a-fA-F]+", t):
        try:
            return int(t, 16)
        except Exception:
            return None
    return None


@dataclass(frozen=True)
class RegisterDef:
    address: int
    desc: str


def _parse_table_defs(lines: list[str], section_title: str) -> list[RegisterDef]:
    # Find section start
    start_idx = -1
    for i, ln in enumerate(lines):
        if ln.strip().startswith(section_title):
            start_idx = i
            break
    if start_idx < 0:
        return []

    defs: dict[int, RegisterDef] = {}
    in_table = False
    for ln in lines[start_idx + 1 :]:
        s = ln.strip()
        if s.startswith("## ") or s.startswith("# "):
            break
        if s.startswith(">"):
            break
        if not s:
            if in_table:
                break
            continue

        if not s.startswith("|"):
            continue

        if s.startswith("| ---"):
            in_table = True
            continue

        in_table = True
        parts = s.split("|")
        if len(parts) < 4:
            continue
        addr_cell = parts[1].strip()
        desc_cell = parts[2].strip()

        if not addr_cell or addr_cell.startswith("..."):
            continue
        if desc_cell.startswith("..."):
            desc_cell = ""

        def _add(a: int) -> None:
            defs.setdefault(a, RegisterDef(address=a, desc=desc_cell))

        if "~" in addr_cell:
            left, right = addr_cell.split("~", 1)
            left_v = _parse_hex_maybe(left)
            if left_v is None:
                continue
            right_s = right.strip()
            if right_s.startswith("(") or "(" in right_s:
                _add(left_v)
                continue
            right_v = _parse_hex_maybe(right_s)
            if right_v is None:
                _add(left_v)
                continue
            if right_v < left_v:
                left_v, right_v = right_v, left_v
            if right_v - left_v > 4096:
                _add(left_v)
                _add(right_v)
                continue
            for a in range(left_v, right_v + 1):
                _add(a)
        else:
            v = _parse_hex_maybe(addr_cell)
            if v is not None:
                _add(v)

    return [defs[k] for k in sorted(defs.keys())]


def load_register_defs_from_basic_md(md_path: str | Path) -> list[RegisterDef]:
    """
    Parse register definitions from:
      doc/oriigin/device_comm_protocol_basic.md
    """
    p = Path(md_path)
    if not p.exists():
        return []
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    return _parse_table_defs(lines, "## 四、主要状态寄存器")


def load_register_defs_from_socket_md(md_path: str | Path) -> list[RegisterDef]:
    """
    Parse register definitions from:
      doc/oriigin/device_comm_protocol_socket.md
    """
    p = Path(md_path)
    if not p.exists():
        return []
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    return _parse_table_defs(lines, "# 云平台读取寄存器")


def load_register_addresses_from_basic_md(md_path: str | Path) -> list[int]:
    return [d.address for d in load_register_defs_from_basic_md(md_path)]
