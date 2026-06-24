# FEAT-0049 BMS 4G 移动端云端详情链路 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-06-12
- related_feature: FEAT-0049
- version: v0.1.0

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
- 4G BMS OTA 数据包 ACK 检测超时从 20 秒收紧到 3 秒，未收到 ACK 时更快重发同包，匹配 BMS 板端 4 秒超时窗口。
- 4G BMS OTA 后端日志和通信调试日志新增 BOOT 包序号、期望 ACK 序号、ACK 对应包序号、重发次数和 MQTT message id，便于现场排查随机延迟。
- Debug 模式 OTA 日志浮层中，APP 侧 BOOT 日志同步显示 16 位包序号、期望 ACK、ACK requested 和 ACK 对应数据包，复制日志时一并带出。

## 发布范围
- 后端 APP 电池接口。
- UniApp 电池详情页。
- Web 后台 BMS 设备详情面板。
- 后端 MQTT Socket WebSocket 桥接。
- UniApp BMS OTA 运行参数与 MQTT Socket BOOT 帧匹配。
- 后端 4G BMS OTA 慢 ACK/ACK 后下发间隔诊断日志。
- 后端 4G BMS OTA 包序号/QoS1 message id 诊断日志。
- 后端 MQTT Socket owner 高频数据包刷新节流。
- UniApp 4G MQTT Socket 读查询休眠唤醒补发逻辑。
- UniApp 4G BMS OTA runtime options 数据包 ACK 超时。
- UniApp Debug OTA 日志中的 BOOT 包序号字段。

## 回滚
- 回滚后端 Socket WebSocket 桥接、UniApp/Web 详情页透传分支后，可恢复为主动上报兜底展示逻辑。
- 如 retained 回包过滤或慢 ACK 日志影响生产排查，可单独回滚 `backend/internal/api/app_battery.go` 中 BOOT retained 过滤和 `socketBootSessionTrace` 日志增强；MQTT topic、owner 互斥和 APP 控制消息无需同步回滚。
- 如包序号诊断或 owner 刷新节流影响现场排查，可单独回滚 `backend/internal/api/app_battery.go` 的 BOOT 日志字段与 `socketOwnerDataRefreshMinInterval` 节流逻辑，以及 `backend/internal/bmsbridge/boot_debug.go` 的通信日志摘要增强；数据库表结构无需回滚。
- 如休眠唤醒补发在现场造成重复查询干扰，可单独将 `UniMqttSocketBmsTransport` 的 `sleepWakeupResendDelayMs` 调整为 `0` 或回滚该 transport 内的补发逻辑；BLE、写入和 BOOT OTA 不依赖该逻辑。
- 如 3 秒数据包 ACK 超时导致蜂窝网络抖动场景下重发过于频繁，可单独调整 `MQTT_BMS_BOOT_PACKET_ACK_TIMEOUT_MS`；BLE BMS、仪表 OTA 和 BOOT 其他阶段无需同步回滚。
- 如 App Debug 包序号字段造成日志过长，可单独回滚 `boot-ota.ts` 与 `uni-mqtt-socket-transport.ts` 中的 `packetIndexHex/expectedAckHex/requestedHex/ackForPacketHex` 日志增强，不影响 OTA 传输协议。
