from __future__ import annotations

from dataclasses import dataclass

from .register_loader import RegisterDef
from .typed_editors import EditorSpec


@dataclass(frozen=True)
class FieldCodec:
    kind: str
    len_regs: int
    scale: int | None = None


@dataclass(frozen=True)
class RegisterMeta:
    addr: int
    desc: str
    field_start: int
    field_len_regs: int
    field_index: int
    editor: EditorSpec
    codec: FieldCodec


def _infer_field_codec_and_editor(desc: str, field_len_regs: int) -> tuple[FieldCodec, EditorSpec]:
    d_lower = (desc or "").lower()
    # Fixed patterns from socket.md
    if "经度" in desc or "纬度" in desc:
        # WGS84 0.00001 -> scaled int32
        return FieldCodec(kind="scaled_i32", len_regs=2, scale=100000), EditorSpec(kind="float", decimals=5, step=0.00001)
    if "速度" in desc:
        # km/h, 0.001
        return FieldCodec(kind="scaled_u16", len_regs=1, scale=1000), EditorSpec(kind="float", decimals=3, step=0.001)
    if "高度" in desc:
        return FieldCodec(kind="i16", len_regs=1), EditorSpec(kind="i16", step=1)
    if "rssi" in d_lower:
        return FieldCodec(kind="i16", len_regs=1), EditorSpec(kind="i16", step=1)
    if "cell identity" in d_lower or "小区识别码" in desc:
        return FieldCodec(kind="u32", len_regs=2), EditorSpec(kind="u32", placeholder="0~4294967295")

    # Text-ish fields
    if "mac" in d_lower:
        return FieldCodec(kind="mac", len_regs=max(1, field_len_regs)), EditorSpec(kind="mac", placeholder="AA:BB:CC:DD:EE:FF")
    if "iccid" in d_lower or "imei" in d_lower or "版本" in desc or "型号" in desc or "编号" in desc or "编码" in desc:
        # If docs say it's multi-register, treat as ascii field.
        if field_len_regs >= 3:
            return FieldCodec(kind="ascii", len_regs=field_len_regs), EditorSpec(kind="ascii", placeholder="ASCII")
        return FieldCodec(kind="u16", len_regs=1), EditorSpec(kind="u16", step=1)

    # Heuristic for 32-bit numeric fields (4 bytes = 2 regs)
    if field_len_regs == 2:
        if "电流" in desc:
            return FieldCodec(kind="i32", len_regs=2), EditorSpec(kind="i32", placeholder="-2147483648~2147483647")
        return FieldCodec(kind="u32", len_regs=2), EditorSpec(kind="u32", placeholder="0~4294967295")

    # Bitfields/flags often appear as u16/u32; keep as u16 editor
    if "bit" in d_lower or "状态" in desc:
        return FieldCodec(kind="u16", len_regs=1), EditorSpec(kind="u16", step=1)

    return FieldCodec(kind="u16", len_regs=1), EditorSpec(kind="u16", step=1)


def build_register_meta(defs: list[RegisterDef]) -> dict[int, RegisterMeta]:
    meta: dict[int, RegisterMeta] = {}
    for d in defs:
        # Some older defs may not include field grouping; fallback to single.
        field_start = getattr(d, "field_start", d.address)
        field_len_regs = getattr(d, "field_len_regs", 1)
        field_index = getattr(d, "field_index", 0)
        codec, editor = _infer_field_codec_and_editor(d.desc, int(field_len_regs))
        # Ensure codec len matches parsed field length for ascii/mac fields.
        if codec.kind in ("ascii", "mac"):
            codec = FieldCodec(kind=codec.kind, len_regs=int(field_len_regs), scale=codec.scale)
        meta[int(d.address)] = RegisterMeta(
            addr=int(d.address),
            desc=d.desc,
            field_start=int(field_start),
            field_len_regs=int(field_len_regs),
            field_index=int(field_index),
            editor=editor,
            codec=codec,
        )
    return meta
