# MQTT 数据透传说明（原文）

- status: approved
- owner: <owner>
- last_updated: 2026-02-14
- source: `doc/oriigin/mqtt数据透传说明.md`
- version: v1.0.0

> 本文是迁移后的主维护版本。

## 6. 数据透传(Socket通讯）

### 6.1 概述

数据透传功能允许设备通过 MQTT 协议进行原始二进制数据的透传通信。设备连接 MQTT Broker 后，使用两个专用 Topic 进行双向通信：

- **发送 Topic**: 设备向平台/APP 端发送数据
- **接收 Topic**: 设备订阅以接收平台/APP 端下发的数据

所有数据以 16 进制字符串的形式通过 JSON 格式进行传输。

### 6.2 Topic 说明

#### 6.2.1 发送 Topic（设备 → 平台/APP）

- **格式**: `device/socket/tx/{device_id}`
- **说明**: 设备向此 Topic 发布数据，平台/APP 端订阅此 Topic 接收数据；当前 4G BMS 接入中 `{device_id}` 使用 `devices.device_number`，不是数据库 UUID。

#### 6.2.2 接收 Topic（平台/APP → 设备）

- **格式**: `device/socket/rx/{device_id}`
- **说明**: 设备订阅此 Topic 接收平台/APP 端下发的数据；当前 4G BMS 接入中 `{device_id}` 使用 `devices.device_number`，不是数据库 UUID。

**注意**: 本文原始协议中的 `{device_id}` 表示硬件侧 Topic 标识。FJBMS 当前实现统一映射为 `devices.device_number`；数据库 UUID 只用于页面路由、权限校验和后端查询，不得直接拼入 Socket Topic。

### 6.3 QoS 设置

- **推荐**: QoS 1（至少传递一次），确保数据可靠传输
- **可选**: QoS 0（最多传递一次），适用于对实时性要求高、允许少量丢失的场景

### 6.4 消息格式

#### 6.4.1 Payload 格式

所有透传消息的 payload 必须遵循以下 JSON 格式：

```json
{
  "hex": "00AABBCCDDEEFF"
}
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `hex` | String | 是 | 16 进制字符串，表示原始二进制数据。字符串长度必须为偶数（每两个字符代表一个字节） |

#### 6.4.2 数据格式说明

- 所有二进制数据必须转换为 16 进制字符串
- 16 进制字符串使用大写字母（A-F）
- 字符串长度必须为偶数（每两个字符代表一个字节）
- 示例：字节数组 `[0x00, 0xAA, 0xBB, 0xCC]` 转换为字符串 `"00AABBCC"`
