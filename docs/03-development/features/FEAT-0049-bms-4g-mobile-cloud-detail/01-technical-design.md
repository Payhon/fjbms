# FEAT-0049 BMS 4G 移动端云端详情链路 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-07-10
- related_feature: FEAT-0049
- version: v0.1.0

## 1. 后端接口
- 新增 `GET /api/v1/app/battery/current-telemetry/:device_id`。
- 接口先调用 `GetBatteryDetailForApp` 完成终端用户绑定、组织账号、租户权限校验。
- 返回 `is_online`、`last_report_ts`、当前遥测键值 map，以及可解析时的 `bms.snapshot`。
- `/api/v1/app/battery/socket/ws` 首包接收数据库 UUID 和 token，完成鉴权后查询设备详情。
- MQTT Socket Topic 标识使用 `devices.device_number`：订阅 `device/socket/tx/{device_number}`，发布 `device/socket/rx/{device_number}`。数据库 UUID 不允许直接用于 Socket Topic。
- 当 `device_number` 为空时，WebSocket 初始化返回明确错误，不回退到数据库 UUID。
- APP 路由层需显式注册 `GET /api/v1/app/battery/socket/ws`，移动端实时详情与 4G BMS OTA 共用该桥接入口。
- MQTT Socket 桥接收到 `device/socket/tx/{device_number}` 非 retained 上行回包后，后端按设备详情判定 4G 能力；仅 `bms_comm_type=2/3` 或存在 `comm_chip_id` 的设备刷新 `devices.is_online=1` 与在线 TTL。
- 4G Socket 交互置在线以设备侧上行回包为准；APP 仅发布下行请求、Socket 建连或 ping 不触发在线状态，避免离线设备被误判在线。
- `/api/v1/app/battery/socket/ws` 对 `device/socket/tx/{device_number}` 的所有 retained 上行响应直接丢弃，不再只过滤 BOOT OTA 帧，避免历史状态帧满足当前请求。
- bms-bridge 使用独立的 clean session、关闭离线订阅恢复并启用 MQTT 有序投递；这些选项只作用于 bridge，主 MQTT adapter 与模拟器保持原默认配置。
- bms-bridge 按原始 MQTT Topic 设备标识哈希分片，同一物理设备固定进入同一 FIFO worker，DB 映射变化不切换分片，跨设备继续并行；同设备桥接接收时间按毫秒严格递增后随结构化遥测传递。
- MQTT adapter 只在 `source=bms_bridge` 且时间不超过 adapter 接收时间 5 分钟时保留桥接时间，uplink 也只对 bridge metadata 透传该时间；普通 MQTT 设备继续使用原 storage 处理时刻。
- `telemetry_current_datas` 的批量与逐条冲突更新仅接受 `EXCLUDED.ts` 不早于当前行的值，历史表仍保留迟到数据。
- APP 当前遥测响应独立返回 `snapshot_ts`；后端只用 `item.ts >= snapshot_ts` 的逐 key current 覆盖快照。完整 `bms.snapshot` 只有自身时间不早于本次所有 current key 的最新时间时才可整体采用，否则移动端按逐 key current 合成状态。

## 2. 移动端数据流
- 详情页加载 `appBatteryDetail` 后判断 4G 能力：`bms_comm_type=2/3`，或存在 `comm_chip_id`。
- 4G/4G+BLE 设备先并行请求 `current-telemetry` 作为首屏快照，并通过后端 Socket WebSocket 建立 MQTT 透传。
- Socket 建连成功后不再先执行 `readUuid()` 预读；直接创建 `BmsClient` 并由后台轮询执行 `readAllStatus()`，减少进入详情后的首帧等待。
- 连接 Socket 前后的 `disconnectAll` 允许保留当前遥测合成出的 `status`，避免首屏快照被清空回加载态。
- `current-telemetry` 若在实时 `readAllStatus()` 已返回后才完成，不覆盖 `dataSourceMode=realtime` 下的实时状态。
- 每次详情加载生成 session generation；设备详情、当前遥测、连接、轮询和重连的异步结果在提交前校验 generation 与设备 ID，页面卸载后统一失效。
- 当前遥测请求记录 request sequence、发起时的 realtime success sequence 与 `last_report_ts` 水位；旧请求、设备不匹配响应、实时恢复后才返回的云端响应和时间倒退响应全部丢弃。fallback 的云端上报时间还必须不早于最后一次实时成功时间（允许 5 秒端云时钟偏差）。
- 已有实时帧时，单次 MQTT 状态读取失败保留最后实时状态；仅连续失败达到阈值且最后实时成功超过保护窗口后才允许云端兜底。尚无实时首帧时仍允许云端快照快速填充。
- fallback 请求同时绑定发起它的 realtime client、polling generation 与暂停状态；切入参数/历史页、换连接或恢复实时后，在途 fallback 不得提交。`cloud_mode` 只允许在无实时 client 时请求和续轮询。
- 页面卸载设置永久 disposed latch 并清理页面延迟任务；旧扫码、仪表重连和 relay 命令必须同时匹配页面生命周期、详情 session、原 Socket task 与原 BMS client。
- 4G/4G+BLE 设备通过 `BmsClient.readAllStatus()` 实时读取仪表盘、电芯和参数数据。
- 4G MQTT 透传中的普通 BMS 寄存器读写保持与 BLE 完全一致的 BMS 帧协议，例如读配置寄存器 `0x0400` 使用功能码 `0x03`。
- 仅 4G 模块专有寄存器 `0x0900~0x0923` 使用云平台读指令 `SOCKET_READ=0x0F`。
- 透传连接或实时读取失败后，降级调用当前遥测接口显示主动上报兜底数据。
- 若返回 `bms.snapshot`，直接作为 `BmsStatus`；否则从当前遥测摘要键合成局部 `BmsStatus` 供仪表盘组件使用。
- 兜底模式下详情页以固定间隔轮询当前遥测，保持面板数据刷新。
- MQTT 实时读取 `readAllStatus()` 成功后，移动端同步将当前详情态 `is_online` 置为 `1`，使顶部状态立即显示 4G 在线；后端持久状态由 Socket 上行回包同步。
- 详情页新增 `bmsDataLoading` 首帧读取状态：
  - 连接建立后、`status` 仍为空时显示仪表盘加载卡片；
  - 首帧 `readAllStatus()` 或云端 `bms.snapshot` 返回后隐藏加载态；
  - 断开连接、离线或进入参数页暂停轮询时清理加载态。
- 参数设置页基础分组采用“先读数据，后展开”：
  - 单体设置、总压设置、电流设置、温度设置首次点击时仅显示分组标题右侧加载图标；
  - 对应分组 `readParamsByKeys()` 完成后再设置展开状态；
  - 已加载分组后续展开/收起不再重复读取。

## 3. 4G BMS OTA 数据流
- 参数页 BMS OTA 入口对 `connType=mqtt` 开放，但仍要求 `props.client` 已就绪，离线或仅云端兜底模式不执行 OTA。
- OTA 包检查继续使用 BMS OTA 包接口；4G BMS 不复用 FEAT-0051 的 4G 模块升级包。
- OTA 目标地址按设备类型先判定：BMS 设备使用 `0x01`，仪表设备使用 `0xFC`。
- 4G BMS OTA 通过 `UniMqttSocketBmsTransport.request()` 发送 BOOT 帧，协议命令与蓝牙 BMS OTA 一致。
- MQTT 透传 OTA 使用独立运行参数：更长的包 ACK/收尾超时、最小帧间隔、包间延迟和页边界延迟，以适配蜂窝网络与 MQTT 转发链路。
- Socket Transport 的 BOOT 响应匹配兼容 finalize `0x54` 收到数据包 ACK `0x53` 的旧设备行为，并兼容仪表 BOOT 回包源地址 `0xFD`。

## 4. Web 端数据流
- 后台 BMS 面板进入 4G 设备详情后自动建立 MQTT Socket 透传，使用与移动端一致的 BMS 协议解析。
- 手动按钮保留为重新连接/断开实时透传。
- `WebMqttSocketBmsTransport` 默认透传普通 `0x03` BMS 帧；只有请求区间完全落在 `0x0900~0x0923` 时才使用 `SOCKET_READ=0x0F` 云平台读指令。

## 5. 电芯数据
- 电芯列表只来自 `cell.voltagesMv` 或 `bms.snapshot.cell.voltagesMv`。
- 如果设备只上报最高/最低/压差摘要，不生成虚假单体列表，只显示明确空态。

## 6. 兼容策略
- BLE-only 设备维持现有主动连接和状态上报逻辑。
- 4G+BLE 设备在详情页优先使用 4G MQTT 透传实时读取。
- 用户侧连接状态在 `connType=mqtt` 时统一显示 4G 图标与“已连接”；内部仍保留 `realtime`、`cloud_fallback`、`offline` 数据源状态用于逻辑分支。
- 参数页暂停轮询、仪表会话、BLE 暖连接、BMS OTA 与 Socket owner 互斥逻辑不参与云端状态仲裁，保持既有行为。
