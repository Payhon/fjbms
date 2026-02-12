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
    # If a row in docs represents a multi-register field, these identify the field group.
    field_start: int
    field_len_regs: int
    field_index: int


def _parse_byte_len_to_regs(byte_len_cell: str) -> int | None:
    s = (byte_len_cell or "").strip()
    if not s:
        return None
    # Only accept a plain integer byte length (e.g. "4"). Expressions like "1+1" / "2*S" are ignored.
    if not re.fullmatch(r"\d+", s):
        return None
    byte_len = int(s, 10)
    if byte_len <= 0:
        return None
    return (byte_len + 1) // 2


def _parse_table_defs(lines: list[str], section_title: str, desc_col: int, byte_len_col: int | None) -> list[RegisterDef]:
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
        if len(parts) <= desc_col:
            continue
        addr_cell = parts[1].strip()
        desc_cell = parts[desc_col].strip()
        byte_len_cell = ""
        if byte_len_col is not None and len(parts) > byte_len_col:
            byte_len_cell = parts[byte_len_col].strip()

        if not addr_cell or addr_cell.startswith("..."):
            continue
        if desc_cell.startswith("..."):
            desc_cell = ""

        def _add_field(start: int, reg_count: int) -> None:
            for i in range(reg_count):
                a = start + i
                defs.setdefault(
                    a,
                    RegisterDef(
                        address=a,
                        desc=desc_cell,
                        field_start=start,
                        field_len_regs=reg_count,
                        field_index=i,
                    ),
                )

        if "~" in addr_cell:
            left, right = addr_cell.split("~", 1)
            left_v = _parse_hex_maybe(left)
            if left_v is None:
                continue
            right_s = right.strip()
            if right_s.startswith("(") or "(" in right_s:
                _add_field(left_v, 1)
                continue
            right_v = _parse_hex_maybe(right_s)
            if right_v is None:
                _add_field(left_v, 1)
                continue
            if right_v < left_v:
                left_v, right_v = right_v, left_v
            if right_v - left_v > 4096:
                _add_field(left_v, 1)
                _add_field(right_v, 1)
                continue
            _add_field(left_v, int(right_v - left_v + 1))
        else:
            v = _parse_hex_maybe(addr_cell)
            if v is not None:
                reg_count = 1
                regs = _parse_byte_len_to_regs(byte_len_cell) if byte_len_col is not None else None
                if regs is not None and regs > 1:
                    reg_count = regs
                _add_field(v, reg_count)

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
    # basic.md table columns:
    # | 地址(1) | 名称(2) | 字节描述(3) | 字节长度(4) | ...
    return _parse_table_defs(lines, "## 四、主要状态寄存器", desc_col=2, byte_len_col=4)


def load_register_defs_from_socket_md(md_path: str | Path) -> list[RegisterDef]:
    """
    Parse register definitions from:
      doc/oriigin/device_comm_protocol_socket.md
    """
    p = Path(md_path)
    if not p.exists():
        return []
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    # socket.md table columns:
    # | 地址(1) | 名称(2) | 长度(字节)(3) | ...
    return _parse_table_defs(lines, "# 云平台读取寄存器", desc_col=2, byte_len_col=3)


def load_register_addresses_from_basic_md(md_path: str | Path) -> list[int]:
    return [d.address for d in load_register_defs_from_basic_md(md_path)]
