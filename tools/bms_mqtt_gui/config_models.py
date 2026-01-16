from __future__ import annotations

from dataclasses import dataclass

from . import protocol


@dataclass(frozen=True)
class ProtoConfig:
    host_address: int = 0xFE
    slave_address: int = 0x01
    read_function: int = protocol.FUNC_READ_HOLDING  # 0x03 / 0x04
    write_function: int = protocol.FUNC_WRITE_MULTIPLE  # 0x10 by default
    report_function: int = 0xDD  # project backend default
    report_format: str = "write"  # write | read | read_addr_qty
    crc_mode: protocol.CRCMode = "source"

