# FEAT-0049 BMS 4G 移动端云端详情链路 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-30
- related_feature: FEAT-0049
- version: v0.1.0

## 1. 后端接口
- 新增 `GET /api/v1/app/battery/current-telemetry/:device_id`。
- 接口先调用 `GetBatteryDetailForApp` 完成终端用户绑定、组织账号、租户权限校验。
- 返回 `is_online`、`last_report_ts`、当前遥测键值 map，以及可解析时的 `bms.snapshot`。
- `/api/v1/app/battery/socket/ws` 首包接收数据库 UUID 和 token，完成鉴权后查询设备详情。
- MQTT Socket Topic 标识使用 `devices.device_number`：订阅 `device/socket/tx/{device_number}`，发布 `device/socket/rx/{device_number}`。数据库 UUID 不允许直接用于 Socket Topic。
- 当 `device_number` 为空时，WebSocket 初始化返回明确错误，不回退到数据库 UUID。

## 2. 移动端数据流
- 详情页加载 `appBatteryDetail` 后判断 4G 能力：`bms_comm_type=2/3`，或存在 `comm_chip_id`。
- 4G/4G+BLE 设备优先通过后端 Socket WebSocket 建立 MQTT 透传，使用 `BmsClient.readAllStatus()` 实时读取仪表盘、电芯和参数数据。
- 4G MQTT 透传中的普通 BMS 寄存器读写保持与 BLE 完全一致的 BMS 帧协议，例如读配置寄存器 `0x0400` 使用功能码 `0x03`。
- 仅 4G 模块专有寄存器 `0x0900~0x0923` 使用云平台读指令 `SOCKET_READ=0x0F`。
- 透传连接或实时读取失败后，降级调用当前遥测接口显示主动上报兜底数据。
- 若返回 `bms.snapshot`，直接作为 `BmsStatus`；否则从当前遥测摘要键合成局部 `BmsStatus` 供仪表盘组件使用。
- 兜底模式下详情页以固定间隔轮询当前遥测，保持面板数据刷新。
- 详情页新增 `bmsDataLoading` 首帧读取状态：
  - 连接建立后、`status` 仍为空时显示仪表盘加载卡片；
  - 首帧 `readAllStatus()` 或云端 `bms.snapshot` 返回后隐藏加载态；
  - 断开连接、离线或进入参数页暂停轮询时清理加载态。
- 参数设置页基础分组采用“先读数据，后展开”：
  - 单体设置、总压设置、电流设置、温度设置首次点击时仅显示分组标题右侧加载图标；
  - 对应分组 `readParamsByKeys()` 完成后再设置展开状态；
  - 已加载分组后续展开/收起不再重复读取。

## 3. Web 端数据流
- 后台 BMS 面板进入 4G 设备详情后自动建立 MQTT Socket 透传，使用与移动端一致的 BMS 协议解析。
- 手动按钮保留为重新连接/断开实时透传。
- `WebMqttSocketBmsTransport` 默认透传普通 `0x03` BMS 帧；只有请求区间完全落在 `0x0900~0x0923` 时才使用 `SOCKET_READ=0x0F` 云平台读指令。

## 4. 电芯数据
- 电芯列表只来自 `cell.voltagesMv` 或 `bms.snapshot.cell.voltagesMv`。
- 如果设备只上报最高/最低/压差摘要，不生成虚假单体列表，只显示明确空态。

## 5. 兼容策略
- BLE-only 设备维持现有主动连接和状态上报逻辑。
- 4G+BLE 设备在详情页优先使用 4G MQTT 透传实时读取。
- 前端显示区分 `MQTT透传实时`、`主动上报兜底`、`离线/无数据`。
