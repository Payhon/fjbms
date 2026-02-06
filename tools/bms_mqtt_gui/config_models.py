from __future__ import annotations

from dataclasses import dataclass

from . import protocol


@dataclass(frozen=True)
class ProtoConfig:
    host_address: int = 0xFE
    slave_address: int = 0xFA
    read_function: int = protocol.FUNC_CLOUD_SOCKET  # 0x0F per socket doc
    write_function: int = protocol.FUNC_WRITE_MULTIPLE  # 0x10 by default
    report_function: int = protocol.FUNC_CLOUD_SOCKET  # 0x0F per socket doc
    report_format: str = "read_addr_qty"  # doc: data starts with start+qty
    crc_mode: protocol.CRCMode = "source"
