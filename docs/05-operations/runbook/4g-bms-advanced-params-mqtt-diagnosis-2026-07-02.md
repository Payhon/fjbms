# 4G BMS 高级参数 MQTT 直连排查记录（2026-07-02）

## 1. 排查对象

- 生产环境时间：2026-07-02 15:30~15:36（Asia/Shanghai）
- 设备序列号 / `device_number`：`36011161145053593437373030124A57`
- `device_id`：`0d3056f5-f556-c126-5c0e-5442f41f83dd`
- `tenant_id`：`d616bcbb`
- `bms_comm_type`：`2`（4G BMS）
- `comm_chip_id`：`862415074075760`
- 电池型号：`FJ-JC24S120A-25010-A01`
- 生产库状态：`is_online=1`，`device_batteries.updated_at=2026-07-02 15:30:32.689808+08`
- 最近 24 小时 `bms_bridge_comm_logs`：1554 条，最新到 `2026-07-02 15:30:33.558609+08`

## 2. MQTT Topic 与消息格式

直连 MQTT 使用和移动端 WebSocket 桥接相同的设备 topic：

- APP/云端下发到设备：`device/socket/rx/36011161145053593437373030124A57`
- 设备返回到云端：`device/socket/tx/36011161145053593437373030124A57`

下发 payload 使用 JSON 包装：

```json
{"hex":"7F55FE01030100000185F6FD"}
```

普通 BMS 参数寄存器使用功能码 `0x03`，源地址 `0xFE`，目标地址 `0x01`。只有 4G 模块专有寄存器 `0x0900~0x0923` 使用功能码 `0x0F`，目标地址 `0xFA`。

## 3. 第一次混合测试：先对照，再读高级参数

测试策略：订阅 `tx` topic 后，按顺序发布 2 个对照请求和 7 个高级参数请求。每个请求最多等待 12 秒；本轮脚本固定在 1.2 秒后补发同帧，因此该轮会产生部分人为重复响应，只用于观察设备响应窗口，不作为移动端精确时序。

| 时间 | 动作 | Topic | 消息 / 响应 | 结果 |
| --- | --- | --- | --- | --- |
| 15:31:57.295 | RX retained | `device/socket/tx/...30124A57` | `0xFF byteCount=56` | broker retained 上一条主动上报 |
| 15:31:58.297 | TX | `device/socket/rx/...30124A57` | `{"hex":"7F55FE01030100000185F6FD"}`，读 `0x0100 qty=1` | 15:31:58.980 返回 `7F5501FE030218022791FD`，RTT 682ms |
| 15:31:59.529 | TX | `device/socket/rx/...30124A57` | `{"hex":"7F55FEFA0F0900002443C7FD"}`，读 4G 模块 `0x0900 qty=36` | 12 秒内无响应 |
| 15:32:11.534 | TX | `device/socket/rx/...30124A57` | `{"hex":"7F55FE01030454000DC4EFFD"}`，高级其他 `0x0454 qty=13` | 12 秒内无响应 |
| 15:32:23.540 | TX | `device/socket/rx/...30124A57` | `{"hex":"7F55FE01030500001044CAFD"}`，电池组编号 `0x0500 qty=16` | 15:32:24.469 返回 `byteCount=32` |
| 15:32:24.003 | RX | `device/socket/tx/...30124A57` | `0xFF byteCount=112` | 主动上报开始 |
| 15:32:24.951 | RX | `device/socket/tx/...30124A57` | `0xFF byteCount=56` | 主动上报尾包 |
| 15:32:24.763 | TX | `device/socket/rx/...30124A57` | `{"hex":"7F55FE0103053A0036E51DFD"}`，DTU 域名端口 `0x053A qty=54` | 15:32:26.562 返回 `byteCount=108` |
| 15:32:26.563 | TX | `device/socket/rx/...30124A57` | `{"hex":"7F55FE010300010001D5CAFD"}`，系统串数 `0x0001 qty=1` | 15:32:28.507 返回 `0018` |
| 15:32:28.507 | TX | `device/socket/rx/...30124A57` | `{"hex":"7F55FE010300040001C5CBFD"}`，电池类型 `0x0004 qty=1` | 本轮匹配受到前一条补发重复响应影响；准确值见第二次复测 |
| 15:32:29.727 | TX | `device/socket/rx/...30124A57` | `{"hex":"7F55FE010300300006C5C7FD"}`，容量 `0x0030 qty=6` | 15:32:32.550 返回 `000000C8000000C0000000C0` |
| 15:32:32.551 | TX | `device/socket/rx/...30124A57` | `{"hex":"7F55FE0103003E0001E5C6FD"}`，功能配置 `0x003E qty=1` | 15:32:34.558 返回 `00C8` |

生产库 `bms_bridge_comm_logs` 同一时间窗可见返回帧：

- `15:31:59.023099`：`functionCode=3 byteCount=2 dataHex=1802`
- `15:32:24.049058`：`functionCode=255 byteCount=112` 主动上报
- `15:32:24.513094`：`functionCode=3 byteCount=32`
- `15:32:26.606010`：`functionCode=3 byteCount=108`
- `15:32:28.547561`：`functionCode=3 byteCount=2 dataHex=0018`
- `15:32:32.595202`：`functionCode=3 byteCount=12`
- `15:32:34.602054`：`functionCode=3 byteCount=2 dataHex=00C8`

本轮现象：`readSn` 能立即返回；但在下一次主动上报前，`0x0F 0x0900` 和第一条高级参数 `0x0454` 均超时。主动上报到达后，后续普通 `0x03` 高级参数连续返回。

## 4. 第二次复测：只发高级参数，按移动端补发逻辑

第二轮不发送 `0x0F 0x0900`，只发送移动端“设置 > 高级参数”会读取的普通 `0x03` 区间；且只在 1.2 秒后仍未匹配时才补发，贴近 `UniMqttSocketBmsTransport` 的 wakeup resend 行为。

| 时间 | 下发 payload | 说明 | 响应时间 | 响应 hex |
| --- | --- | --- | --- | --- |
| 15:35:06.316 | `{"hex":"7F55FE01030454000DC4EFFD"}` | `0x0454 qty=13`，其他配置 | 15:35:08.815，RTT 2499ms | `7F5501FE031A0D16141E1464414641500105A0A0A0A00105FF0A033C0014FF0A0119FD` |
| 15:35:08.815 | `{"hex":"7F55FE01030500001044CAFD"}` | `0x0500 qty=16`，电池组编号 | 15:35:09.833，RTT 1017ms | `7F5501FE0320FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF88C5FD` |
| 15:35:09.833 | `{"hex":"7F55FE0103053A0036E51DFD"}` | `0x053A qty=54`，DTU 域名端口 | 15:35:10.931，RTT 1097ms | `7F5501FE036CFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF748AFD` |
| 15:35:10.931 | `{"hex":"7F55FE010300010001D5CAFD"}` | `0x0001 qty=1`，串数配置 | 15:35:11.833，RTT 901ms | `7F5501FE03020018AC5AFD` |
| 15:35:11.833 | `{"hex":"7F55FE010300040001C5CBFD"}` | `0x0004 qty=1`，电池类型 | 15:35:12.967，RTT 1134ms | `7F5501FE030201FFED80FD` |
| 15:35:12.967 | `{"hex":"7F55FE010300300006C5C7FD"}` | `0x0030 qty=6`，容量配置 | 15:35:13.852，RTT 884ms | `7F5501FE030C000000C8000000C0000000C01BB4FD` |
| 15:35:13.852 | `{"hex":"7F55FE0103003E0001E5C6FD"}` | `0x003E qty=1`，功能配置 | 15:35:14.852，RTT 999ms | `7F5501FE030200C8ADC6FD` |

生产库同窗 `uplink_parsed` 记录：

- `15:35:08.856857`：`functionCode=3 byteCount=26`
- `15:35:09.877307`：`functionCode=3 byteCount=32`
- `15:35:10.976803`：`functionCode=3 byteCount=108`
- `15:35:11.876164`：`functionCode=3 byteCount=2 dataHex=0018`
- `15:35:12.936127`：`functionCode=3 byteCount=2 dataHex=01FF`
- `15:35:13.897492`：`functionCode=3 byteCount=12`
- `15:35:14.895652`：`functionCode=3 byteCount=2 dataHex=00C8`

结论：在没有前置超时请求阻塞的情况下，该设备高级参数普通 `0x03` 读链路可以稳定在 1~3 秒内返回。

## 5. 状态大包补测

为确认详情页实时状态读取链路是否也通，补测 `readAllStatus()` 中的两个大包：

| 时间 | 下发 payload | 说明 | 响应 |
| --- | --- | --- | --- |
| 15:36:05.629 | `{"hex":"7F55FE0103010000358421FD"}` | `0x0100 qty=53`，状态固定区，期望 `byteCount=106` | 15:36:08.008 返回 `byteCount=106`，RTT 2379ms |
| 15:36:08.009 | `{"hex":"7F55FE01030141004F55D6FD"}` | `0x0141 qty=79`，状态动态区，期望 `byteCount=158` | 15:36:09.070 返回 `byteCount=158`，RTT 1061ms |

生产库同窗：

- `15:36:08.045063`：`functionCode=3 byteCount=106`
- `15:36:09.117393`：`functionCode=3 byteCount=158`

结论：该设备当前完整状态大包也可以实时返回。

## 6. 问题定位

1. 本次直连没有复现“只要读取高级参数就必须等 1 分钟”。当只发送高级参数 `0x03` 读寄存器时，所有高级参数均在 0.9~2.5 秒返回。
2. “高级参数约 1 分钟才显示”不应理解为高级参数走了主动上报 fallback。移动端代码中高级参数 `loadKeys()` 只调用 `readParamsByKeys()` 实时读寄存器，失败时置空；没有从 `telemetry_current_datas` 或主动上报快照回填高级参数的逻辑。
3. 慢加载更像是移动端 transport 串行队列被前置请求占住：
   - `UniMqttSocketBmsTransport` 对所有 request 做串行队列。
   - 切到参数页会暂停后续轮询，但不会取消已经在途的 `readAllStatus()`。
   - 如果切页时前面已有一个大包读取、4G 模块 `0x0F` 读取或其它请求正在等待超时，高级参数会排在它后面。
   - 直连测试中 `0x0F 0x0900 qty=36` 两次均未返回；如果移动端现场有任何路径先发该请求，会消耗单次约 10~12 秒，并拖慢后续参数。
4. 本次混合测试里，`0x0F` 超时后第一条高级参数 `0x0454` 也超时；但复测证明 `0x0454` 本身可读。说明当时更可能是设备/模块处理窗口或前置请求状态导致，而不是 `0x0454` 地址不支持。

## 7. 后续建议

1. 在移动端 Debug 日志里补齐非 BOOT 的 request trace：记录 `functionCode/startAddress/quantity/expectedByteCount/queueWaitMs/timeoutMs/rttMs`，这样现场能直接看到“高级参数前面排了哪个请求”。
2. 对参数页切换时的在途状态读取做处理：进入参数页时不仅 `stopPolling()`，还需要避免当前 `readAllStatus()` 继续占住 transport 队列；可考虑引入 request cancellation、generation token，或参数读取前等待/清理已过期的状态轮询。
3. `0x0900~0x0923` 4G 模块信息读取当前对这台设备无响应，应与高级参数读取隔离，不要放在同一个设置页加载队列里同步等待。
4. 普通 `0x03` 单寄存器响应不携带起始地址；如果同一请求被补发且响应晚到，后续同样 `byteCount=2` 的 pending 只能靠串行时序匹配，存在被延迟重复响应污染的风险。现场 Debug 日志应特别标出补发次数和 late response。

## 8. 已落地移动端优化（2026-07-02）

本次根据上述证据先做低风险体验优化，不强行取消 transport 已在途请求：

1. `BmsClient.readAllStatus()` 增加 `shouldContinue` 检查点。移动端进入参数/设置页暂停轮询后，旧状态读取最多等待当前在途请求结束，不再继续排后续 `readSn -> 0x0100 -> 0x0135 -> 0x0141` 子请求。
2. 详情页把轮询取消识别为预期状态，不再记录为 poll failed，也不触发首帧失败处理或 4G 当前遥测 fallback 刷新。
3. `readParamsByKeys()` 支持 `timeoutMs`，UniApp 在 `connType=mqtt` 下读取参数分组时传入 5 秒单组超时，避免个别无响应区间长时间阻塞后续高级参数分组。
4. 加载态同步尊重 `pollingPaused`，避免进入设置页后旧轮询的 finally 又把首帧加载态打开。
5. 已补充协议断言：参数短超时会传到 transport；状态轮询暂停后不会继续排后续状态子请求。

仍未处理的边界：当前请求已经发到 MQTT 后不会被强制取消，原因是普通 `0x03` 响应不带起始地址，直接丢弃/抢占 pending 可能让迟到短响应污染后续同 `byteCount` 参数读取。若后续仍出现明显等待，应优先补充非 BOOT request trace，确认具体排队请求和 RTT。
