from __future__ import annotations

import json
from dataclasses import dataclass


class PayloadError(Exception):
    pass


@dataclass(frozen=True)
class SocketPayload:
    hex: str


def bytes_to_hex_upper(b: bytes) -> str:
    return b.hex().upper()


def decode_socket_payload(payload: bytes) -> str:
    """
    Compatible with backend bms_bridge decodeSocketHex:
    - Prefer JSON: {"hex": "..."}
    - Else fallback to raw string
    """
    try:
        obj = json.loads(payload.decode("utf-8", errors="strict"))
        if isinstance(obj, dict) and isinstance(obj.get("hex"), str) and obj["hex"].strip():
            return obj["hex"].strip()
    except Exception:
        pass
    s = payload.decode("utf-8", errors="ignore").strip()
    if not s:
        raise PayloadError("empty payload")
    return s


def encode_socket_payload(hex_str: str) -> bytes:
    body = {"hex": hex_str.upper()}
    return json.dumps(body, ensure_ascii=True, separators=(",", ":")).encode("utf-8")


def hex_to_bytes(hex_str: str) -> bytes:
    s = hex_str.strip().replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
    if len(s) % 2 != 0:
        raise PayloadError(f"hex string length must be even, got {len(s)}")
    try:
        return bytes.fromhex(s)
    except ValueError as e:
        raise PayloadError(f"invalid hex string: {e}") from e

