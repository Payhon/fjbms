# FEAT-0074 技术设计

- status: review
- owner: payhon
- last_updated: 2026-09-16

## 协议与入口

复用 `BmsClient.syncTime(timestampSeconds, options)`，验证 uint32 整数后拆分为两个大端寄存器，经 `writeRegisters` 透传请求参数。调用参数为 `timeoutMs=3000`、`writeApiTimeoutMs=3000`、`disableAlternateWriteRetry=true`；其他写命令不改变超时与重试默认值。

`common/ble/ble-time-sync.ts` 提供 `syncBleBmsTimeOnce(client, connectionMac, bmsCommType)`，仅 AC 且类型严格为 1 时允许发送。WeakMap 按 client 保存尝试 Promise，发送前登记；并发等待同一任务，失败也保留尝试记录。未知类型直接跳过，不占用尝试次数。

## 连接生命周期

- `connectBleClient` 接收真实 `bmsCommType`，在 BLE connect 完成（包括 notify 和预热）并缓存连接后校时；缓存复用及并发连接同样走共享入口。
- `BleClientEntry.connectionMac` 保留实际连接 MAC，与可能从仪表透传读取的 BMS 身份 MAC 分开；未知用 null，不回退身份 MAC。
- 首页与详情、OTA 后重连透传设备类型。详情接管温连接前等待校时；后续云端资料明确纯蓝牙时，当前 BLE 连接可以补校时。OTA 独占期间不补发。
- 配网在取得设备类型后，用广播/扫码/原生 MAC 调用入口；iOS UUID 不当成 MAC。缓存交接保留同一 client 与实际连接 MAC。
- 不把 handoff 缺失通信类型默认成 1。物理重连创建新 client，因此重新尝试；正常复用不重发。
- 校时前后维持连接取消、缓存有效性、页面会话检查，避免旧连接被接管；异常仅记录诊断日志，不阻断业务。

## 兼容与限制

无外部接口、数据库或 UI 变化，不添加定时校时、重试、依赖。复用串行 BLE 队列及 OTA 独占保护。校时成功以现有写应答解析为准；设备实际 RTC 更新须由真机验证。
