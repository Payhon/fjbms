# BMS Modbus over MQTT GUI (PyQt5)

本工具用于在 MQTT 的 `device/socket/*` 透传 Topic 上，发送/接收“富嘉 BMS 帧”，并用表格维护寄存器值；同时支持模拟从机自动响应读/写请求、以及按选中寄存器进行主动上报。

## 运行

1) 安装依赖：

```bash
python -m pip install -r tools/bms_mqtt_gui/requirements.txt
```

2) 启动：

```bash
python tools/bms_mqtt_gui/app.py
```

## 说明（与文档差异）

项目内后端实现（`backend/internal/bms/protocol`）默认使用 **CRC 覆盖范围从 source address 开始**（即从帧第 3 个字节开始，不含 0x7F 0x55 头码）；而 `doc/oriigin/device_comm_protocol_basic.md` 中部分示例/描述存在“从 target address 开始”的说法。

为了兼容，本工具提供可切换的 CRC 计算范围：
- `source+...`：从 source address 开始（默认，兼容后端 bmsbridge / bms-sim）
- `target+...`：从 target address 开始（按文档描述）

