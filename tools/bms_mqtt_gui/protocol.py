from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional


FrameType = Literal[
    "error",
    "read_response",
    "write_response",
    "read_request",
    "write_request",
]

CRCMode = Literal["source", "target"]  # CRC region starts at source or target address


FRAME_HEAD0 = 0x7F
FRAME_HEAD1 = 0x55
FRAME_TAIL = 0xFD


FUNC_READ_HOLDING = 0x03
FUNC_READ_INPUT = 0x04
FUNC_CLOUD_SOCKET = 0x0F
FUNC_WRITE_MULTIPLE = 0x10
FUNC_ASSIGN_SLAVE_ADDR = 0x11
FUNC_READ_UUID = 0xFF


class ProtocolError(Exception):
    pass


def crc16_modbus(data: bytes) -> int:
    # Standard Modbus CRC16 (poly 0xA001), little-endian in frame (CRCL, CRCH).
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


def _crc_region(frame_without_crc_and_tail: bytes, crc_mode: CRCMode) -> bytes:
    # frame_without_crc_and_tail includes header bytes.
    if len(frame_without_crc_and_tail) < 5:
        return b""
    if crc_mode == "source":
        return frame_without_crc_and_tail[2:]  # from source address
    return frame_without_crc_and_tail[3:]  # from target address


def _append_crc_and_tail(frame_without_crc: bytearray, crc_mode: CRCMode) -> bytes:
    # frame_without_crc currently includes header bytes and body, but not CRC nor tail.
    crc = crc16_modbus(_crc_region(bytes(frame_without_crc), crc_mode))
    frame_without_crc.append(crc & 0xFF)  # CRCL
    frame_without_crc.append((crc >> 8) & 0xFF)  # CRCH
    frame_without_crc.append(FRAME_TAIL)
    return bytes(frame_without_crc)


def be_u16(v: int) -> bytes:
    return bytes([(v >> 8) & 0xFF, v & 0xFF])


def split_regs_be(data: bytes) -> list[int]:
    if len(data) % 2 != 0:
        raise ProtocolError(f"register data length must be even, got {len(data)}")
    regs: list[int] = []
    for i in range(0, len(data), 2):
        regs.append((data[i] << 8) | data[i + 1])
    return regs


def regs_to_be_bytes(regs: list[int]) -> bytes:
    out = bytearray()
    for v in regs:
        out.extend(be_u16(v & 0xFFFF))
    return bytes(out)


def build_read_request(
    source_addr: int,
    target_addr: int,
    function_code: int,
    start_addr: int,
    quantity: int,
    crc_mode: CRCMode = "source",
) -> bytes:
    frame = bytearray([FRAME_HEAD0, FRAME_HEAD1, source_addr & 0xFF, target_addr & 0xFF, function_code & 0xFF])
    frame.extend(be_u16(start_addr & 0xFFFF))
    frame.extend(be_u16(quantity & 0xFFFF))
    return _append_crc_and_tail(frame, crc_mode)


def build_read_response(
    source_addr: int,
    target_addr: int,
    function_code: int,
    data: bytes,
    crc_mode: CRCMode = "source",
) -> bytes:
    if len(data) > 250:
        data = data[:250]
    frame = bytearray([FRAME_HEAD0, FRAME_HEAD1, source_addr & 0xFF, target_addr & 0xFF, function_code & 0xFF])
    frame.append(len(data) & 0xFF)
    frame.extend(data)
    return _append_crc_and_tail(frame, crc_mode)


def build_write_request(
    source_addr: int,
    target_addr: int,
    function_code: int,
    start_addr: int,
    regs: list[int],
    crc_mode: CRCMode = "source",
) -> bytes:
    quantity = len(regs)
    byte_count = quantity * 2
    if byte_count > 250:
        raise ProtocolError("write request too large: max 250 data bytes")
    frame = bytearray([FRAME_HEAD0, FRAME_HEAD1, source_addr & 0xFF, target_addr & 0xFF, function_code & 0xFF])
    frame.extend(be_u16(start_addr & 0xFFFF))
    frame.extend(be_u16(quantity & 0xFFFF))
    frame.append(byte_count & 0xFF)
    frame.extend(regs_to_be_bytes(regs))
    return _append_crc_and_tail(frame, crc_mode)


def build_write_response(
    source_addr: int,
    target_addr: int,
    function_code: int,
    start_addr: int,
    quantity: int,
    crc_mode: CRCMode = "source",
) -> bytes:
    frame = bytearray([FRAME_HEAD0, FRAME_HEAD1, source_addr & 0xFF, target_addr & 0xFF, function_code & 0xFF])
    frame.extend(be_u16(start_addr & 0xFFFF))
    frame.extend(be_u16(quantity & 0xFFFF))
    return _append_crc_and_tail(frame, crc_mode)


@dataclass(frozen=True)
class ParsedFrame:
    type: FrameType
    source_address: int
    target_address: int
    function_code: int
    raw: bytes

    # Optional fields depending on type
    error_code: Optional[int] = None
    start_address: Optional[int] = None
    quantity: Optional[int] = None
    byte_count: Optional[int] = None
    data: Optional[bytes] = None

    crc_mode_used: Optional[CRCMode] = None


def parse_frame(frame: bytes, crc_mode: CRCMode = "source", allow_crc_fallback: bool = True) -> ParsedFrame:
    if len(frame) < 6:
        raise ProtocolError(f"frame too short: {len(frame)}")
    if frame[0] != FRAME_HEAD0 or frame[1] != FRAME_HEAD1:
        raise ProtocolError("bad frame header")
    if frame[-1] != FRAME_TAIL:
        raise ProtocolError("bad frame tail")
    if len(frame) < 2 + 3 + 2 + 1:
        raise ProtocolError("frame too short for CRC")

    declared_crc = (frame[-2] << 8) | frame[-3]
    body_wo_crc_tail = frame[:-3]  # includes header

    def _check(mode: CRCMode) -> bool:
        calc = crc16_modbus(_crc_region(body_wo_crc_tail, mode))
        return calc == declared_crc

    used_mode = crc_mode
    if not _check(crc_mode):
        if allow_crc_fallback:
            other: CRCMode = "target" if crc_mode == "source" else "source"
            if _check(other):
                used_mode = other
            else:
                calc = crc16_modbus(_crc_region(body_wo_crc_tail, crc_mode))
                raise ProtocolError(f"CRC mismatch (declared=0x{declared_crc:04X}, calc=0x{calc:04X}, mode={crc_mode})")
        else:
            calc = crc16_modbus(_crc_region(body_wo_crc_tail, crc_mode))
            raise ProtocolError(f"CRC mismatch (declared=0x{declared_crc:04X}, calc=0x{calc:04X}, mode={crc_mode})")

    source = frame[2]
    target = frame[3]
    func = frame[4]

    # Error response: function = req + 0x80, length 9
    if len(frame) == 9 and (func & 0x80) != 0:
        return ParsedFrame(
            type="error",
            source_address=source,
            target_address=target,
            function_code=func,
            error_code=frame[5],
            raw=bytes(frame),
            crc_mode_used=used_mode,
        )

    # 12-byte frames can be:
    # - Read request:  [.., func, addrHi, addrLo, qtyHi, qtyLo, crcLo, crcHi, tail]
    # - Write response:[.., func, addrHi, addrLo, qtyHi, qtyLo, crcLo, crcHi, tail]
    if len(frame) == 12:
        start = (frame[5] << 8) | frame[6]
        qty = (frame[7] << 8) | frame[8]
        if func in (FUNC_WRITE_MULTIPLE, FUNC_ASSIGN_SLAVE_ADDR):
            return ParsedFrame(
                type="write_response",
                source_address=source,
                target_address=target,
                function_code=func,
                start_address=start,
                quantity=qty,
                raw=bytes(frame),
                crc_mode_used=used_mode,
            )
        return ParsedFrame(
            type="read_request",
            source_address=source,
            target_address=target,
            function_code=func,
            start_address=start,
            quantity=qty,
            raw=bytes(frame),
            crc_mode_used=used_mode,
        )

    # Write request: [.., func, addrHi, addrLo, qtyHi, qtyLo, byteCount, data..., crcLo, crcHi, tail]
    if len(frame) >= 13:
        start = (frame[5] << 8) | frame[6]
        qty = (frame[7] << 8) | frame[8]
        byte_count = frame[9]
        expected_len = 13 + int(byte_count)
        if expected_len == len(frame):
            data = bytes(frame[10 : 10 + int(byte_count)])
            return ParsedFrame(
                type="write_request",
                source_address=source,
                target_address=target,
                function_code=func,
                start_address=start,
                quantity=qty,
                byte_count=byte_count,
                data=data,
                raw=bytes(frame),
                crc_mode_used=used_mode,
            )

    # Read-like response: [.., func, byteCount, data..., crcLo, crcHi, tail]
    if len(frame) >= 10:
        byte_count = frame[5]
        expected_len = 2 + 3 + 1 + int(byte_count) + 2 + 1
        if expected_len == len(frame):
            data = bytes(frame[6 : 6 + int(byte_count)])
            return ParsedFrame(
                type="read_response",
                source_address=source,
                target_address=target,
                function_code=func,
                byte_count=byte_count,
                data=data,
                raw=bytes(frame),
                crc_mode_used=used_mode,
            )

    raise ProtocolError(f"unknown frame type (func=0x{func:02X}, len={len(frame)})")
