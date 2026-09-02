# FEAT-0049 BMS 4G 移动端云端详情链路 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-09-02
- related_feature: FEAT-0049
- version: v0.2.4

## 用户影响
- 4G BMS 设备在移动端和 Web 端详情页优先使用 MQTT Socket 透传实时读取，仪表盘、电芯和参数数据与 BLE 解析链路保持一致。
- 移动端 4G BMS 详情页先显示当前遥测/快照，后台实时数据返回后覆盖，减少进入详情后的空等时间。
- 4G BMS 设备支持从参数页执行 BMS OTA，升级协议与蓝牙 BMS 一致，经 APP WebSocket 桥接 MQTT 透传。
- 4G MQTT 透传普通 BMS 寄存器保持 `0x03` 读寄存器协议，只有 `0x0900~0x0923` 4G 模块专有寄存器使用云平台 `0x0F` 读指令。
- 参数设置页按连续寄存器范围批量读取，展开单体设置、总压设置等分组时数据整体显示更快。
- 移动端从首页进入设备详情后，连接成功但首帧 BMS 实时数据尚未返回时，会显示加载提示，不再短暂展示空白/零值仪表盘。
- 移动端参数设置基础分组首次展开时会在标题右侧显示加载图标，数据返回后再展开并切回向上箭头。
- 透传失败时仍保留 MQTT 主动上报当前遥测作为兜底，不再因无 BLE 连接而直接显示离线。
- 如果设备未上报单体电芯明细，电芯 Tab 会明确提示未收到明细数据。
- 详情页用户侧连接状态在 4G 链路下统一显示 4G 图标与“已连接”，不暴露内部技术链路。
- 后端会忽略 MQTT Socket 订阅到的 BOOT retained 回包，避免旧 ACK 误参与当前 4G BMS OTA 会话。
- 4G BMS 板无通讯休眠后，移动端首个实时读查询会在短时间无响应时自动补发一次，用于唤醒 BMS 板并继续读取数据。
- 4G BMS OTA 曾将数据包ACK窗口从20秒收紧到3秒，再与BLE统一为900ms；本轮客户验证包调整为600ms，未收到ACK时继续按原重试机制重发同包，最终参数以真机结果为准。
- 4G BMS OTA 后端日志和通信调试日志新增 BOOT 包序号、期望 ACK 序号、ACK 对应包序号、重发次数和 MQTT message id，便于现场排查随机延迟。
- Debug 模式 OTA 日志浮层中，APP 侧 BOOT 日志同步显示 16 位包序号、期望 ACK、ACK requested 和 ACK 对应数据包，复制日志时一并带出。
- 4G BMS 设备通过 MQTT Socket 产生真实上行回包时，后端会刷新设备在线状态；即使当前没有主动遥测上报，移动端详情页实时读数成功后也会显示 4G 在线。
- 仪表盘或电芯页已经显示实时数据后，单次 MQTT 读取超时不再切换到云端旧快照；连续失败超过保护窗口时才使用云端当前遥测兜底，实时恢复后立即切回。
- 切换设备、离开页面或多个云端请求乱序返回时，旧会话和旧时间戳数据不会再覆盖当前设备页面。
- 后端过滤 retained 上行并保证同一设备有序处理；迟到的旧遥测仍可进入历史表，但不能把当前值回退到更早时间。
- `bms.snapshot` 现在携带独立 `snapshot_ts`；后端不会再让旧单键反向覆盖新快照。如果快照早于本次逐项 current 数据，仪表盘和电芯页按较新的逐项数据合成，不再把“某个摘要刚更新”误当成整组快照都新。
- 进入参数/历史页切换轮询策略后，在途云端 fallback 不再改变连接类型或干扰参数读取、历史读取和 OTA；页面卸载后的扫码、仪表重连和 relay 命令也不会复活旧会话。
- 4G BMS 参数设置页进入后约每 10 秒串行读取一次设备状态，首轮同样延后 10 秒，在现场确认的约 15 秒休眠阈值前维持数据交互；历史记录页继续使用 30 秒低频读取。对应 BLE Tab 保持暂停轮询。
- Web 端 4G BMS 电芯页不再把协议无效值 `0xFFFF` 显示为 `65.535 V`；全无效实时数组会回退有效云端数组，部分无效项保留电芯序号并显示为 `-`。
- 4G BMS 在线且移动端通过当前 MQTT Socket 会话成功完成主动读取后，后端会保存该次完整响应作为独立的最近交互快照；设备随后离线时，移动端优先显示这份快照。
- 主动读取失败、超时、旧 Socket 会话、其他账号/租户或非 4G 设备不能更新交互快照；不存在交互快照时继续使用原有主动上报数据，不改变旧客户端行为。
- 相机扫码进入 4G/4G+BLE 设备详情后，页面立即显示“4G 在线”并在后台继续读取；60 秒内所有读取均无有效回包且后端仍离线时才显示“4G 离线”。该宽限只影响本次详情页，不提前改变首页、Web 或其他账号看到的后端在线状态。
- 底部加号扫码/相册识别经 BLE 配网成功并复用暖连接进入详情时，扫码来源不会再因 handoff 快速分支丢失；已绑定直达、UUID 绑定和配网 handoff 三条扫码路径统一执行上述 60 秒在线宽限。

## 发布范围
- 后端 APP 电池接口。
- UniApp 电池详情页。
- Web 后台 BMS 设备详情面板。
- 后端 MQTT Socket WebSocket 桥接。
- UniApp BMS OTA 运行参数与 MQTT Socket BOOT 帧匹配。
- 后端 4G BMS OTA 慢 ACK/ACK 后下发间隔诊断日志。
- 后端 4G BMS OTA 包序号/QoS1 message id 诊断日志。
- 后端 MQTT Socket owner 高频数据包刷新节流。
- 后端 4G MQTT Socket 上行回包置在线逻辑。
- UniApp 4G MQTT Socket 读查询休眠唤醒补发逻辑。
- UniApp 4G 详情实时读取成功后的在线状态同步。
- UniApp 4G BMS OTA runtime options 数据包 ACK 超时。
- UniApp Debug OTA 日志中的 BOOT 包序号字段。
- UniApp 设备详情数据源仲裁与页面会话失效保护。
- 后端 bms-bridge retained 过滤、独立 MQTT 投递配置、同设备 FIFO 分片、桥接接收时间透传与当前遥测单调 upsert。
- 后端 APP 当前遥测 `snapshot_ts` 字段与移动端快照新鲜度判定。
- UniApp 设备详情 Tab 轮询策略、4G 参数页 10 秒保活与历史页 30 秒保活。
- Web BMS 面板电芯电压无效值归一化与数据源回退。
- 后端 APP 4G 主动读取快照接口、Socket owner/session 鉴权和 current-only 原子快照存储。
- UniApp MQTT Socket 会话标识、主动读取快照异步上报和云端 fallback 数据源优先级。
- UniApp 扫码来源透传、4G 详情 60 秒本地在线宽限和 MQTT 当前请求匹配回包通知。

## 回滚
- 回滚后端 Socket WebSocket 桥接、UniApp/Web 详情页透传分支后，可恢复为主动上报兜底展示逻辑。
- 如 retained 回包过滤或慢 ACK 日志影响生产排查，可单独回滚 `backend/internal/api/app_battery.go` 中 BOOT retained 过滤和 `socketBootSessionTrace` 日志增强；MQTT topic、owner 互斥和 APP 控制消息无需同步回滚。
- 如包序号诊断或 owner 刷新节流影响现场排查，可单独回滚 `backend/internal/api/app_battery.go` 的 BOOT 日志字段与 `socketOwnerDataRefreshMinInterval` 节流逻辑，以及 `backend/internal/bmsbridge/boot_debug.go` 的通信日志摘要增强；数据库表结构无需回滚。
- 如休眠唤醒补发在现场造成重复查询干扰，可单独将 `UniMqttSocketBmsTransport` 的 `sleepWakeupResendDelayMs` 调整为 `0` 或回滚该 transport 内的补发逻辑；BLE、写入和 BOOT OTA 不依赖该逻辑。
- 如统一600ms非完成帧应答窗口导致蜂窝网络抖动场景下重发过于频繁，可调整共享 `MOBILE_BOOT_NON_FINALIZE_TIMEOUT_MS` 或恢复按传输类型拆分；无需修改 `0x54` 完成策略。
- 如 App Debug 包序号字段造成日志过长，可单独回滚 `boot-ota.ts` 与 `uni-mqtt-socket-transport.ts` 中的 `packetIndexHex/expectedAckHex/requestedHex/ackForPacketHex` 日志增强，不影响 OTA 传输协议。
- 如 4G 数据交互置在线在现场造成误判，可单独回滚后端 `MarkFourGBatteryOnlineByInteraction` 调用与 UniApp `readAllStatus()` 成功后的 `is_online` 同步；实时数据读取、参数读取和 OTA 透传协议不需要同步回滚。
- 如移动端保护窗口不适配现场网络，可单独调整 `MQTT_CLOUD_FALLBACK_FAILURE_THRESHOLD` 与 `MQTT_REALTIME_STALE_BEFORE_FALLBACK_MS`，或回滚 `detail-data-arbiter` 接入；BLE、仪表、参数和 OTA 链路不依赖该仲裁逻辑。
- 如 bridge 有序消费影响吞吐，可分别回滚 bridge 专用 `DeliveryOptions` 和按设备分片队列；主 MQTT adapter 默认参数未改变。当前遥测时间单调条件可独立回滚且不涉及数据库结构变更。
- 如参数页 10 秒或历史页 30 秒状态读取影响业务操作时延，可单独回滚 `detail-polling-policy` 与 `useBatteryDetail` 的可配置间隔，恢复对应 Tab 暂停轮询；仪表盘、电芯页及后端无需同步回滚。
- 如 Web 电芯无效值归一化与现场私有协议不兼容，可单独回滚 `cell-voltage.ts` 及 BMS 面板接入，不影响后端遥测、MQTT Socket 和 UniApp。
- 如主动读取快照在现场不符合预期，可先回滚 UniApp 的 `interactive_snapshot` 优先级和上报调用，立即恢复原主动上报 fallback；后端独立 current 键不会进入普通 `current` 合成，也不涉及数据库结构回滚。
- 如扫码在线宽限不符合现场口径，可单独回滚 `entry_source=scan` 透传、`scan-four-g-online-policy` 与 Transport 匹配响应回调，恢复直接展示后端 `is_online`；后端在线判定、MQTT 轮询和参数/历史保活无需回滚。
