# bms-bridge 说明文档

## 1. 文档目的

本文档基于当前仓库代码实现，说明 `bms-bridge` 的：

- 配置项
- 启动方式
- 工作流程
- 数据流向
- 转发逻辑
- 告警事件逻辑
- 调试日志行为
- 当前实现边界与注意事项

本文档描述的是当前代码行为，不是理想设计稿。

---

## 2. 进程定位

`bms-bridge` 是一个独立进程，不随 `fjbms` 主进程自动启动。

作用是：

1. 订阅 BMS 设备通过 MQTT `device/socket/tx/{device_id}` 上传的原始 hex 协议数据
2. 将 hex 解码为 BMS 通讯帧
3. 按寄存器地址解析为扁平字段和部分语义化字段
4. 根据 rules 配置拆分为遥测、属性、事件
5. 再转发到下游 IoT 平台的 MQTT 接口
6. 可选同步一部分最新数据到数据库 `device_batteries`

入口文件：

- `backend/cmd/bms-bridge/main.go`

核心实现：

- `backend/internal/bmsbridge/config.go`
- `backend/internal/bmsbridge/bridge.go`
- `backend/internal/bmsbridge/rules.go`
- `backend/configs/bms-bridge-rules.yml`

---

## 3. 启动方式

### 3.1 命令

```bash
cd backend
go run ./cmd/bms-bridge -config ./configs/conf-dev.yml
```

### 3.2 启动流程

`cmd/bms-bridge/main.go` 的流程如下：

1. 读取 `-config`
2. 初始化基础应用能力：
   - 配置
   - logger
   - database
3. 从配置中加载 `bms_bridge.*`
4. 若 `bms_bridge.enabled=false`，进程直接退出
5. 创建 `Bridge`
6. 建立 MQTT 连接并订阅上行 Topic
7. 启动 worker 和状态清理协程
8. 等待 `SIGINT/SIGTERM`
9. 收到退出信号后取消上下文、断开 MQTT、等待 worker 退出

---

## 4. 配置说明

### 4.1 主配置节点

主配置位于：

- `backend/configs/conf.yml`
- `backend/configs/conf-dev.yml`
- `backend/configs/conf-prod.yml`

配置节点为：

```yaml
bms_bridge:
```

### 4.2 配置项清单

#### 4.2.1 开关

```yaml
bms_bridge:
  enabled: true
```

- 含义：是否启用 bridge
- 默认值：`true`

#### 4.2.2 MQTT 连接与转发配置

```yaml
bms_bridge:
  mqtt:
    broker:
    user:
    pass:
    client_id:
    subscribe_topic:
    subscribe_qos:
    telemetry_topic:
    telemetry_qos:
    attributes_topic_prefix:
    attributes_qos:
    events_topic_prefix:
    events_qos:
    publish_timeout_ms:
```

说明：

- `broker`
  - 若未配置，回退到全局 `mqtt.broker`
  - 若仍为空，再回退到 `mqtt.access_address`
- `user` / `pass`
  - 若未配置，回退到全局 `mqtt.user` / `mqtt.pass`
- `client_id`
  - 默认：`fjbms-bms-bridge`
- `subscribe_topic`
  - 默认：`device/socket/tx/+`
- `subscribe_qos`
  - 默认：`1`
- `telemetry_topic`
  - 下游遥测 Topic
  - 默认：`devices/telemetry`
- `telemetry_qos`
  - 默认：`0`
- `attributes_topic_prefix`
  - 下游属性 Topic 前缀
  - 默认：`devices/attributes/`
  - 实际发布时会拼接 message id
- `attributes_qos`
  - 默认：`1`
- `events_topic_prefix`
  - 下游事件 Topic 前缀
  - 默认：`devices/event/`
- `events_qos`
  - 默认：`1`
- `publish_timeout_ms`
  - MQTT 发布超时毫秒数
  - 默认：`3000`

#### 4.2.3 报告帧配置

```yaml
bms_bridge:
  report:
    function_code: 221
    status_start_address: 256
```

说明：

- `function_code`
  - 默认 `0xDD`（十进制 221）
  - 用于识别 BMS 主动上报帧
- `status_start_address`
  - 默认 `0x100`（十进制 256）
  - 当报告帧本身不携带寄存器起始地址时，默认视作从该地址开始

#### 4.2.4 rules 配置

```yaml
bms_bridge:
  rules:
    path: ./configs/bms-bridge-rules.yml
    reload_interval_sec: 5
```

说明：

- `path`
  - rules 文件路径
- `reload_interval_sec`
  - 文件热加载检查周期
  - 默认 `5`

#### 4.2.5 worker 配置

```yaml
bms_bridge:
  workers:
    concurrency: 8
    queue_size: 4096
```

说明：

- `concurrency`
  - worker 数量
  - 默认 `8`
- `queue_size`
  - 入站消息队列长度
  - 默认 `4096`

#### 4.2.6 事件状态缓存配置

```yaml
bms_bridge:
  events:
    state_ttl_minutes: 60
```

说明：

- 用于告警/保护位变化检测时的旧值缓存
- 默认 `60` 分钟

### 4.3 日志配置

`bms-bridge` 的 DEBUG 日志是否开启，不由 `bms_bridge` 节点控制，而是由全局日志级别控制：

```yaml
log:
  level: debug
```

当 `log.level=debug` 时，会输出 bridge 的详细调试日志，包括：

- 原始 hex
- 解析后的帧结构
- 语义化状态 JSON
- 扁平化 payload JSON

当 `log.level=info` 或更高时，这些 DEBUG 日志不会打印。

---

## 5. rules 文件说明

rules 文件默认位于：

- `backend/configs/bms-bridge-rules.yml`

结构如下：

```yaml
version: 1
default:
  telemetry:
  attributes:
  events:
  db_sync:
by_device:
```

### 5.1 telemetry

`telemetry` 表示要转发到下游遥测接口的字段映射。

示例：

```yaml
telemetry:
  soc: energy.socPct
  soh: energy.sohPct
  packCellSumVoltageV: electrical.packCellSumVoltageV
```

含义：

- 左边：下游平台看到的 key
- 右边：bridge 内部解析后的字段路径

### 5.2 attributes

`attributes` 表示要转发到下游属性接口的字段映射。

示例：

```yaml
attributes:
  seriesCount: meta.seriesCount
  hardwareModel: identity.hardwareModel
```

### 5.3 events

`events` 用于控制告警/保护位变化是否转成事件。

示例：

```yaml
events:
  enabled: true
  emit_on_change: true
  method_prefix: "bms."
  track_key_prefixes:
    - status.alarmStatus.
    - status.protectionStatus.
```

说明：

- 只在值变化时发送事件
- 默认跟踪：
  - `status.alarmStatus.*`
  - `status.protectionStatus.*`

### 5.4 db_sync

`db_sync` 用于把部分解析结果同步到数据库 `device_batteries`。

示例：

```yaml
db_sync:
  enabled: true
  device_batteries:
    soc: energy.socPct
    imei: socket.imei
```

### 5.5 by_device

`by_device` 可针对指定设备覆盖默认 rules。

---

## 6. 工作流程

### 6.1 总体流程

```text
设备 -> MQTT(device/socket/tx/{device_id})
     -> bms-bridge 订阅
     -> 提取 hex
     -> hex 解码为 frame bytes
     -> 解析协议帧
     -> 按寄存器地址拆出 registers
     -> 生成 flat map
     -> 可选语义化解析
     -> 按 rules 拆分 telemetry / attributes / events / db_sync
     -> MQTT 转发到 IoT 平台
     -> 可选同步 device_batteries
```

### 6.2 Topic 订阅

bridge 启动后会订阅：

```text
device/socket/tx/+
```

然后从 Topic 中取出 `{device_id}`。

### 6.3 MQTT payload 格式

bridge 支持两种输入形式：

1. JSON

```json
{"hex":"7F55...FD"}
```

2. 纯字符串

```text
7F55...FD
```

### 6.4 hex 解码

支持自动忽略以下分隔符：

- 空格
- Tab
- 换行
- `-`
- `:`

### 6.5 协议帧解析

bridge 会做：

1. 帧头校验
2. 帧尾校验
3. CRC16-Modbus 校验
4. 识别帧类型

当前支持的主要帧类型：

- `ReadFrame`
- `WriteRequestFrame`
- `ReadRequestFrame`
- `WriteFrame`
- `ErrorFrame`

其中真正进入“寄存器拆分 + 转发”的主要是：

- `ReadFrame`
- `WriteRequestFrame`

---

## 7. 功能码支持与转发逻辑

## 7.1 会被转发的功能码

当前代码实现下，下列报文可以进入“拆寄存器并转发”流程：

### A. `0x0F`

前提：

- 报文为 `ReadFrame`
- `Data` 内部格式是：

```text
[startAddress(2 bytes)] + [quantity(2 bytes)] + [register data]
```

此时 bridge 会：

1. 从 `Data` 中提取 `startAddress`
2. 按 `quantity` 拆寄存器
3. 继续做扁平化与语义化解析

### B. `0x03`

前提：

- 报文为 `ReadFrame`
- `Data` 内部同样带：

```text
[startAddress(2 bytes)] + [quantity(2 bytes)] + [register data]
```

如果满足这个模式，bridge 也会把它按寄存器地址解析并转发。

注意：

- 标准 `0x03` 回复本身通常只包含 `byteCount + data`
- 但当前生产环境里，部分设备上传的 `0x03` 数据前 4 字节实际携带了 `startAddress + quantity`
- bridge 现已兼容这种模式

### C. `0xDD`

分两种情况：

1. `ReadFrame`
   - 直接把 `Data` 视为寄存器数据
   - 起始地址使用 `bms_bridge.report.status_start_address`
2. `WriteRequestFrame`
   - 使用帧内 `StartAddress`
   - 使用帧内 `Data`

## 7.2 不会被转发的情况

以下情况不会进入下游遥测/属性转发：

1. Topic 不是 `device/socket/tx/{device_id}` 格式
2. payload 不是可解码 hex
3. 帧头/帧尾/CRC 校验失败
4. 帧类型不是 `ReadFrame` / `WriteRequestFrame`
5. `ReadFrame` 虽然是 `0x03` 或 `0x0F`，但 `Data` 里无法提取出 `startAddress + quantity + register data`
6. 不符合 rules 里定义的字段映射

---

## 8. 寄存器解析与语义化逻辑

### 8.1 扁平化寄存器

无论是否能做更高层语义化，bridge 都会先生成：

- `report.startAddress`
- `report.quantity`
- `reg.0xXXXX`

例如：

```json
{
  "report.startAddress": 256,
  "report.quantity": 4,
  "reg.0x0100": 4128,
  "reg.0x0101": 286
}
```

### 8.2 4G Socket 扩展寄存器语义化

当起始地址落在 `0x900~0x923` 范围时，还会额外解析：

- `socket.longitude`
- `socket.latitude`
- `socket.speedKmh`
- `socket.altitudeM`
- `socket.rssi`
- `socket.tac`
- `socket.cellId`
- `socket.imei`
- `socket.iccid`
- `socket.moduleVersion`

### 8.3 状态区 `0x100` 语义化

当 `report.startAddress == 0x100` 且寄存器长度满足最小要求时，会调用状态解析器，将状态区语义化为：

- `meta.*`
- `energy.*`
- `timing.*`
- `electrical.*`
- `temperature.*`
- `cell.*`
- `status.*`
- `identity.*`

然后再通过 `FlattenStatus()` 合并回 flat map。

这部分可用于：

- 遥测
- 属性
- 告警事件
- 数据库同步

---

## 9. 下游转发逻辑

### 9.1 遥测转发

函数：

- `publishTelemetry()`

默认 Topic：

```text
devices/telemetry
```

默认 QoS：

```text
0
```

消息结构：

```json
{
  "device_id": "xxx",
  "values": {
    "soc": 88,
    "currentA": 12.3
  }
}
```

### 9.2 属性转发

函数：

- `publishAttributes()`

默认 Topic 前缀：

```text
devices/attributes/
```

实际 Topic：

```text
devices/attributes/{messageId}
```

默认 QoS：

```text
1
```

消息结构：

```json
{
  "device_id": "xxx",
  "values": {
    "hardwareModel": "xxx",
    "protocolVersion": 1
  }
}
```

### 9.3 告警/保护事件转发

函数：

- `emitEventsFromStatusChange()`

逻辑：

1. 使用 `BoolStateStore` 保存上一次布尔状态
2. 仅在值发生变化时生成事件
3. 默认跟踪：
   - `status.alarmStatus.*`
   - `status.protectionStatus.*`

默认 Topic 前缀：

```text
devices/event/
```

事件结构：

```json
{
  "device_id": "xxx",
  "values": {
    "method": "bms.status.alarmStatus.packOverVoltageAlarm",
    "params": {
      "key": "status.alarmStatus.packOverVoltageAlarm",
      "active": true,
      "ts": 1710000000
    }
  }
}
```

注意：

- 告警类信息不是走 telemetry/attributes
- 而是走 event Topic

### 9.4 数据库同步

如果 `db_sync.enabled=true`，bridge 还会把部分字段同步到 `device_batteries`。

默认包括：

- `soc`
- `soh`
- `ble_mac`
- `item_uuid`
- `longitude`
- `latitude`
- `speed`
- `altitude`
- `rssi`
- `tac`
- `cell_id`
- `imei`
- `iccid`
- `module_sw_version`

用途：

- 给后台/API 查询“最新值”
- 给设备管理页面提供附加设备信息

---

## 10. 数据流向说明

## 10.1 入站数据流

```text
设备
  -> MQTT Broker
  -> Topic: device/socket/tx/{device_id}
  -> bms-bridge
```

## 10.2 bridge 内部处理流

```text
MQTT message
  -> queue
  -> worker
  -> decodeSocketHex
  -> DecodeHexString
  -> ParseFrame
  -> extractReadFramePayload / WriteRequestFrame
  -> SplitIntoRegistersBE
  -> flattenRegisters
  -> decodeSocketRegisters / ParseStatusRegisters
  -> applyRules
```

## 10.3 出站数据流

```text
flat map
  -> telemetry values -> devices/telemetry
  -> attribute values -> devices/attributes/{id}
  -> event values -> devices/event/{id}
  -> db sync -> device_batteries
```

---

## 11. DEBUG 调试日志

当全局日志级别为 `debug` 时，bridge 会打印以下调试日志：

1. 接收到的 MQTT 消息长度与 Topic
2. 原始 `raw_hex`
3. `parsed frame json`
4. `parsed status json`
5. `parsed payload json`

### 11.1 parsed frame json

为了避免 Go 默认把 `[]byte` 打成 base64，当前已转成 hex 字段：

- `dataHex`
- `rawHex`

### 11.2 parsed payload json

这是最适合排查问题的日志，里面会看到：

- `report.startAddress`
- `report.quantity`
- `reg.0x....`
- `socket.*`
- `meta.*`
- `energy.*`
- `electrical.*`
- `status.*`
- `identity.*`

说明：

- 只有当报文能被拆成“带地址的寄存器块”时，才会有完整 payload JSON
- 若只是普通响应但没有地址信息，bridge 无法判断寄存器映射关系，则不会生成语义化 payload

---

## 12. 已知实现边界与注意事项

### 12.1 `0x03` 并非所有场景都能语义化

bridge 当前对 `0x03` 的支持是：

- 只有当 `ReadFrame.Data` 里实际包含：

```text
[startAddress][quantity][register data]
```

时，才会按寄存器地址做拆分。

如果设备上传的是纯标准 `0x03` 回复格式，只带数据不带地址，bridge 无法从响应本身反推出寄存器区间，因此不会语义化。

### 12.2 历史记录协议未接入 bridge

当前 bridge 主要处理：

- `0x0F`
- `0x03`
- `0xDD`

历史记录相关 `0x4C / 0x4D` 目前不在 bridge 转发链路中。

### 12.3 事件只在“状态变化”时产生

告警/保护信息不是每次全量重发，而是：

- 先缓存旧状态
- 检测变化
- 有变化才发事件

### 12.4 rules 是热加载的

bridge 会按 `rules.reload_interval_sec` 周期检查 rules 文件是否变更。

这意味着：

- 改 rules 后通常无需重启进程
- 但配置主文件 `bms_bridge.*` 变化仍需重启进程

---

## 13. 推荐排障步骤

### 场景 A：收到数据但没转发

建议依次排查：

1. 是否订阅到了正确 Topic
2. `raw_hex` 是否完整
3. CRC 是否通过
4. `parsed frame json` 的 `functionCode` 是否在 bridge 支持范围
5. `parsed payload json` 是否生成
6. rules 文件里是否有对应字段映射

### 场景 B：有寄存器值，但没有语义化字段

重点检查：

1. `report.startAddress` 是多少
2. 是否落在 `0x100` 状态区
3. 是否落在 `0x900~0x923` socket 扩展区
4. `0x03` 报文是否真的带了 `startAddress + quantity`

### 场景 C：告警没有下发到下游

重点检查：

1. `status.alarmStatus.*` / `status.protectionStatus.*` 是否出现在 `parsed payload json`
2. 是否真的发生了布尔值变化
3. rules 的 `events.enabled` 是否打开
4. `track_key_prefixes` 是否包含对应前缀

---

## 14. 当前默认转发内容摘要

### 遥测

- `soc`
- `soh`
- `packCellSumVoltageV`
- `vPackV`
- `currentA`
- `ambientC`
- `chargeMosC`
- `dischargeMosC`
- `highestCellVoltageMv`
- `lowestCellVoltageMv`
- `maxCellVoltageDiffMv`

### 属性

- `seriesCount`
- `cellTempCount`
- `hardwareVersion`
- `softwareVersion`
- `protocolVersion`
- `hardwareModel`
- `batteryGroupId`
- `boardCode`
- `bluetoothMac`

### 事件

- `status.alarmStatus.*` 变化
- `status.protectionStatus.*` 变化

### 数据库同步

- 电池基础状态字段
- 蓝牙 MAC
- 板编码
- 4G 定位与模组信息

---

## 15. 结论

`bms-bridge` 当前是一个“BMS 原始协议帧 -> 寄存器块 -> 语义字段 -> IoT 平台消息”的专用桥接进程。

它的核心能力包括：

1. 订阅 BMS 的 MQTT 透传上行数据
2. 校验并解析 BMS 帧
3. 支持 `0x0F`、`0xDD`、以及带地址头的 `0x03`
4. 将寄存器解析为遥测、属性、事件和数据库同步字段
5. 通过 rules 文件实现可配置转发
6. 在 DEBUG 模式下输出足够详细的原始与语义化日志

如果后续继续扩展 bridge，建议优先补充：

1. `0x4C / 0x4D` 历史记录协议接入
2. 对更多地址段的语义化解析
3. 更明确的报文来源类型区分（主动上报 / 查询响应 / 控制响应）
4. 更完整的规则说明与样例
