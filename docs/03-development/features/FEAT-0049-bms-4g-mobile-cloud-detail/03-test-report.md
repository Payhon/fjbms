# FEAT-0049 BMS 4G 移动端云端详情链路 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-09-12
- related_feature: FEAT-0049
- version: v0.2.11

## 2026-09-12 动态ACK超时本地验证

- 结果：累计27项本地脚本通过（原26项回归加新增可控时钟测试），不是硬件验收。覆盖Boot时序/运行参数/动态超时、实际BLE/MQTT transport、BLE能力与取消、MQTT响应匹配/唤醒/fjia2、缓存释放、OTA页面会话、仪表恢复、日志、OTA目标策略、轮询以及扫描/参数/4G兼容路径。
- 可控时钟：0x50～0x53无ACK在0/800/1250/1700ms发送、2150ms耗尽；0x54在0/5000/5450/5900ms发送、6350ms耗尽。首发799ms、完成4999ms和重发449ms收到ACK即结束等待，无残留定时器。用户补充的完成重发450ms已覆盖，非每次5秒。
- 验证同包重试、三次共享恢复预算、status=3重复ACK、status=1重新准备及其800/450重试、所有非ACK错误立即失败、0x50与4G进入Boot的耗尽兼容。模拟1151 ACK后300ms页保护，1152丢ACK仍重发1152，不叠加页等待；64/128/256/512/1024字节页边界回归通过。
- 页面真实SFC处理函数验证BLE/MQTT五种命令的首次与重发timeoutMs均透传，旧450ms上限不再截断800ms；零宽限不调度Android读探测，非零宽限的底层兼容测试仍保留。
- TypeScript检查与params-tab.vue/detail.vue的SFC脚本和模板编译通过；根仓库和UniApp的git diff --check通过。未修改普通连接超时或BLE会话恢复逻辑。
- Android/iOS微信小程序不退出进程连续20次、App三链路、4G连续20次和实际版本/弱信号验证仍待完成，保持in_progress。未提交、推送或部署。

新增时序测试无需安装依赖，在fjbms-uniapp目录执行：

```sh
node -e 'const fs=require("fs"),ts=require("typescript");require.extensions[".ts"]=(m,f)=>m._compile(ts.transpileModule(fs.readFileSync(f,"utf8"),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText,f);require("./common/lib/bms-protocol/boot-ota-dynamic-timeout.test.ts")'
pnpm exec tsc --noEmit --pretty false
git diff --check
```


## 2026-09-10 BLE OTA 恢复兼容边界

- FEAT-0046新增的关闭屏障、原生断连订阅和30秒/最多两次恢复仅应用于BLE。共享详情页的MQTT连接、云端回退、参数轮询、后台命令转发及OTA协议策略不作调整。
- MQTT/4G仍使用670ms同包重试、300ms页保护、完整数据ACK门槛和单发5秒完成窗口；既有工作区修改保留，本轮未再次修改MQTT transport或共享Boot引擎。
- Boot/运行参数/transport及MQTT响应匹配、唤醒、fjia2和页面会话回归通过；新断言确认MQTT不会进入BLE恢复。真机4G/App及iOS/Android冒烟仍待完成，保持in_progress。
- 发布和回滚只涉及FEAT-0046本轮移动端差异，无后端/数据库/接口/依赖变更；本轮不提交、推送或部署。

## 测试用例
- 后端：当前遥测接口可通过已绑定/组织可见设备查询数据。
- 后端：无 `bms.snapshot` 时仍返回当前摘要遥测 map。
- UniApp：4G-only 设备进入详情页不发起 BLE 连接，不因主动连接失败显示离线。
- UniApp：4G/4G+BLE 设备进入详情页优先使用 MQTT Socket 透传实时读取，透传失败后显示主动上报兜底数据。
- UniApp：4G 设备详情顶部状态不暴露技术链路，Socket 透传实时和主动上报兜底都显示 4G 图标与“已连接”。
- UniApp：4G 设备进入详情页先展示当前遥测/快照，后台实时 `readAllStatus()` 返回后覆盖，不因 Socket 切换清空首屏。
- UniApp：4G Socket 建连不再先执行 `readUuid()` 预读。
- UniApp：4G BMS OTA 通过 MQTT Socket Transport 发送 BOOT 帧，并使用 4G 专用超时/节流参数。
- 后端：同一 4G BMS 只能有一个移动端实时 MQTT Socket owner，第二个连接返回 occupied，不挤掉当前连接。
- 后端：owner TTL 可由 `ping` 和下行发布请求刷新，WebSocket 关闭时只释放同 `session_id` owner。
- 后端：未声明 `mqtt_socket_owner_v1` 的旧客户端成功连接不收到 `socket_ready` 控制消息。
- UniApp：第二个账号遇到 occupied 后切到云端上报只读模式，顶部显示友好轻提示。
- UniApp：occupied 只读模式下参数写入、虚拟容量写入和 BMS OTA 显示专用提示且不发送透传指令。
- UniApp：连接成功但首帧 BMS 实时状态未返回时，仪表盘展示加载提示而不是空白/零值数据。
- UniApp：参数设置基础分组首次展开时先显示标题右侧加载图标，读取完成后再展开。
- Web：4G 设备进入 BMS 面板自动使用 MQTT Socket 透传实时读取，手动按钮可重新连接/断开透传。
- 后端：Socket WebSocket 首包使用数据库 UUID 鉴权，实际 MQTT topic 使用 `devices.device_number`。
- 后端：APP 电池路由注册 `/api/v1/app/battery/socket/ws`。
- UniApp：有当前遥测但无 `cell.voltagesMv` 时，仪表盘有摘要数据，电芯 Tab 显示明确空态。
- UniApp：扫码或首页列表进入 4G/4G+BLE 详情后立即显示在线，60 秒内无任何匹配有效回包且后端仍离线时才显示离线；组织设备列表、手动 BLE 搜索与 BLE-only 设备不启用宽限。
- UniApp：只有当前 MQTT 请求匹配的有效帧刷新扫码在线保护；控制消息、心跳、非法帧、意外帧和旧会话迟到帧不得刷新。

## 当前结果
- [x] `go test ./internal/bmsbridge ./internal/bms/protocol ./internal/bms/status ./internal/service`：通过。
  - 覆盖用户提供的 `0x0141` 上报帧，解析出 14 路单体电压、4 路电芯温度。
  - 校验最高电压 `3002mV`、最低电压 `2973mV`、压差 `29mV`、单体和 `41.816V`。
  - 温度寄存器按当前协议实现公式 `raw - 2731` 后除以 10，结果为 `27.0/28.0/27.0/27.0°C`。
- [x] `cd frontend && pnpm build`：通过；构建期间存在既有 `eval` 与 unocss 图标加载警告，不影响本次构建结果。
- [x] `cd frontend && pnpm typecheck`：通过。
- [x] 后台 Web 4G 设备详情交互检查：BMS 面板默认云端遥测展示，不再自动连接参数直连；连接状态拆分为 MQTT 上报、云端订阅、参数通道。
- [x] 后台 Web 云端刷新检查：手动刷新会重新拉取电池基础信息、当前遥测和历史图表；云端遥测 WebSocket 关闭/异常后会自动重连。
- [x] `pnpm --dir fjbms-uniapp -s exec tsc --noEmit`：通过。
- [x] 生产 `bms-bridge` 更新：`make deploy-bridge-prod` 已同步二进制、主配置和 `backend/configs` 目录，`make update-bridge-prod` 已追加发布短 `0x0100` 防污染保护，systemd 服务 `fjbms-bms-bridge` 为 `active`。
- [x] 生产配置核验：`/www/fjia/fjbms/backend/bms-bridge/configs/bms-bridge-rules.yml` 已包含 `cell.voltagesMv`、`temperature.cellTempsC`、`cellVoltagesMv`、`cellTempsC`、电芯最高/最低索引等发布键。
- [x] 生产污染数据清理：已删除目标设备因短 `0x0100` 兼容补齐写入的 `65535/null` 电芯数组缓存，避免后台电芯 Tab 展示无效数组。
- [ ] 生产等待下一条 `0x0141`：截至 `2026-04-27 12:51:38`，目标设备发布后仅收到 `0x0100` 摘要状态帧；最近一条 `0x0141` 电芯明细帧仍是 `2026-04-27 11:18:49`，需要下一条真实 `0x0141` 到达后确认 `cell.voltagesMv` 写入当前遥测。
- [x] `go test ./internal/model ./internal/api ./internal/service ./router/apps`：通过。
- [x] 生产只读确认目标设备 `36011161145053593437373030124930`：
  - `device_id=05de8897-838e-8913-45d5-24b968abc913`
  - 当前仅存在 `highestCellVoltageMv`、`lowestCellVoltageMv`、`maxCellVoltageDiffMv`
  - 未查询到 `bms.snapshot`、`cell.voltagesMv`、`temperature.cellTempsC`
  - 最近匹配上报时间：`2026-04-27 11:18:55`（Asia/Shanghai）
- [x] 生产只读确认目标设备 `36011161145053593437373030124930` 当前绑定与遥测：
  - `device_id=05de8897-838e-8913-45d5-24b968abc913`
  - `device_batteries.item_uuid=36011161145053593437373030124930`
  - `bms_comm_type=2`，`activation_status=ACTIVE`，`transfer_status=USER`
  - 当前用户已存在 `device_user_bindings` 绑定记录，重复扫码添加时后端返回 `device already bound to current user`
  - `telemetry_current_datas` 已有 `soc/soh/currentA/packCellSumVoltageV/cell.voltagesMv/temperature.cellTempsC` 等当前值
- [x] 生产接口探测：
  - `GET https://cloud.fjiaenergy.com/api/v1/app/battery/detail/:device_id` 未登录返回 401，路由存在
  - `GET https://cloud.fjiaenergy.com/api/v1/app/battery/current-telemetry/:device_id` 未登录返回 404，生产后端暂未发布 App 专用当前遥测路由
  - `GET https://cloud.fjiaenergy.com/api/v1/telemetry/datas/current/:device_id` 未登录返回 401，通用当前遥测路由存在，可作为移动端兼容 fallback
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`：通过。
- [x] `cd backend && go test ./internal/api ./internal/service ./router/apps`：通过；仅出现 macOS SDK 中 `IOMasterPort` 废弃警告。
- [x] 生产后端与前端更新：`make update-backend-prod`、`make update-frontend-prod` 均已完成；`fjbms-backend` systemd 服务为 `active (running)`。
- [x] 后端 Socket WebSocket 生产实测：使用数据库 UUID `05de8897-838e-8913-45d5-24b968abc913` 初始化 `/api/v1/app/battery/socket/ws`，设备详情解析出的 `device_number=36011161145053593437373030124930` 可正常完成透传。
- [x] 生产 4G Socket 响应实测：旧实现下发送读 UUID 和读 `0x0100` 均收到 `0x0F` 响应帧，证明后端桥接 Topic 已能到达目标设备；后续已根据协议修正普通 BMS 读寄存器不应统一转 `0x0F`。
- [x] 生产问题定位：实测 `0x0F` 响应的 `byteCount` 为字节数，例如 `byteCount=0x3C` 时整帧长度为 69 字节；原前端按寄存器数执行 `byteCount * 2`，导致帧长度不匹配并被丢弃。
- [x] UniApp/Web 协议解析修复：`SOCKET_READ=0x0F` 响应统一按 `byteCount` 字节截取数据，不再翻倍。
- [x] UniApp 二次剥离修复：`parseFrame` 不再提前剥离 `0x0F` 数据区的 `startAddress/quantity`，避免 `BmsClient` 后续解析时误把寄存器数据当地址头。
- [x] 生产轮询超时复现：目标设备读 `0x0100` 响应耗时约 4~7 秒，原 2500ms 会提前超时并错过响应。
- [x] 生产响应范围复现：读 `0x0100, qty=1` 实际返回 `0x0100, qty=54`，读动态区 `0x0141` 返回已有 28 个寄存器；客户端已改为缓存整段响应并按请求范围取交集。
- [x] 生产 `readAllStatus()` 顺序模拟：`readSn -> head cache -> tail` 跑通，读出 `seriesCount=14`、`cellTempCount=4`，动态区 28 个寄存器可进入状态解析。
- [x] UniApp/Web 4G Socket 默认请求超时调整为 10000ms，串行请求队列在单次超时后可恢复。
- [x] 参数配置寄存器无响应结论修正：生产无响应发生时目标设备已离线，不作为 4G Socket 不支持 `0x0400` 等配置寄存器的证据。
- [x] UniApp/Web 响应匹配修复：`SOCKET_READ=0x0F` pending 请求增加寄存器区间校验，避免主动上报的 `0x0100/0x0141` 状态帧误匹配参数读取请求。
- [x] UniApp 参数设置页修正：撤回 MQTT 实时模式下的“不支持”提示和跳过读取逻辑，在线设备会继续真实读取参数配置寄存器。
- [x] 4G MQTT 透传功能码修正：普通状态/参数寄存器保持 BLE 同款 `0x03` 读寄存器帧，仅 `0x0900~0x0923` 4G 模块专有寄存器使用云平台 `SOCKET_READ=0x0F`。
- [x] UniApp/Web Transport 修正：默认不再将 `0x03` 请求转换为 `0x0F`；仅请求区间完全落在 `0x0900~0x0923` 时执行自动转换。
- [x] 参数设置读取性能优化：UniApp/Web 直连模式改为 `readParamsByKeys()` 按连续寄存器范围批量读取，避免展开单体/总压等分组时逐项串行显示。
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`：通过。
- [x] UniApp 首帧等待态与参数分组加载态类型校验：`cd fjbms-uniapp && pnpm exec tsc --noEmit` 通过。
- [x] UniApp 4G 连接状态展示口径调整：`connType=mqtt` 时顶部胶囊统一显示 4G 图标与“已连接”，不再展示 `MQTT透传实时` 或 `主动上报兜底`。
- [x] `cd frontend && pnpm typecheck`：通过。
- [x] `make update-frontend-prod`：解析修复已重新构建并替换生产前端；构建期间仅有既有 `eval` 与 unocss 图标加载警告。
- [x] 生产 WebSocket 复测：初始化后收到 `0x0F` 透传状态帧，发送读 UUID 后收到目标设备响应。
- [ ] UniApp 真机复测：待使用包含本次解析修复的移动端包进入 4G 设备详情，确认状态为 `MQTT透传实时`，仪表盘/电芯/参数来自 `readAllStatus()`。
- [ ] UniApp 真机交互复测：待确认从首页进入详情时首帧等待卡片展示正常，参数分组加载图标在数据返回后切为向上箭头并展开。
- [ ] Web 浏览器复测：待进入同一 4G 设备 BMS 面板确认仪表/电芯数据来自 `readAllStatus()`，并验证重新连接和断开实时透传。
- [ ] `go test ./...`：失败在既有环境依赖用例，非本次改动包；`initialize/test` 空指针，`backend/test` 未设置 `run_env` 导致 DB 为空。
- [x] 2026-06-04 `cd fjbms-uniapp && pnpm exec tsc --noEmit`：通过。
- [x] 2026-06-04 `cd backend && go test ./internal/api ./internal/service ./router/apps`：通过。
- [ ] 2026-06-04 UniApp 真机复测：待使用新包确认 4G BMS 详情核心数据 2 秒内可见，以及后台实时数据覆盖快照。
- [ ] 2026-06-04 4G BMS OTA 真机复测：待使用真实 4G BMS 通过 MQTT Socket 透传执行 BOOT 升级。
- [x] 2026-06-05 生产只读日志确认目标设备 `360111611350535934373730300A354F`：
  - `bms_comm_type=2`，确认是 4G BMS。
  - `bms_bridge_comm_logs` 在 `2026-06-05 10:18:02.929725+08` 与 `2026-06-05 10:18:05.960001+08` 收到两次 `0x50` BOOT 版本响应，响应间隔约 3 秒。
  - 最近 4 小时未查到 `0x51/0x52/0x53/0x54` BOOT 响应，判断移动端需要放宽 4G/MQTT BOOT 时序并兼容 `0x51` timeout。
- [x] 2026-06-05 `cd fjbms-uniapp && pnpm exec tsc --noEmit`：通过。
- [x] 2026-06-05 `git -C fjbms-uniapp diff --check`：通过。
- [ ] 2026-06-05 4G BMS OTA 真机复测：待使用包含本次 BOOT 时序修复的新包，确认 `0x50` 能匹配响应并进入 `0x52/0x53/0x54` 升级流程。
- [x] 2026-06-08 后端相关包回归：`cd backend && go test ./internal/api ./internal/service ./router/apps` 通过。
- [x] 2026-06-08 UniApp occupied 降级类型检查：`cd fjbms-uniapp && pnpm exec tsc --noEmit` 通过。
- [x] 2026-06-08 `git diff --check`：通过。
- [ ] 2026-06-08 真机双账号复测：待使用新包同时进入同一 4G BMS，确认第一个实时连接保持、第二个云端只读、参数/OTA 入口被友好拦截。
- [x] 2026-06-10 UniApp 4G BMS OTA 快速模式与埋点类型检查：`cd fjbms-uniapp && pnpm exec tsc --noEmit` 通过。
- [x] 2026-06-10 后端 WebSocket/MQTT Boot 埋点回归：`cd backend && go test ./internal/api ./internal/service ./router/apps` 通过。
- [x] 2026-06-10 `git diff --check && git -C fjbms-uniapp diff --check && git -C backend diff --check`：通过。
- [ ] 2026-06-10 4G BMS OTA 真机复测：待使用新包升级真实设备，采集 APP `[boot]/[socket]` 日志、后端 `bms mqtt socket boot ...` 日志和 BMS 串口日志，确认 `0x53` 平均间隔与 12 秒重发是否改善。
- [x] 2026-06-10 Debug 模式 OTA 日志浮层类型检查：`cd fjbms-uniapp && pnpm exec tsc --noEmit` 通过。
- [x] 2026-06-11 Debug 模式 OTA 日志浮层裁剪修复：日志面板已从 OTA 升级弹窗内部移到页面级 fixed 浮层，正文高度按窗口动态计算，避免受外层弹窗高度约束。
- [x] 2026-06-11 Debug 日志浮层布局修复类型检查：`cd fjbms-uniapp && pnpm exec tsc --noEmit` 通过。
- [x] 2026-06-11 `git diff --check && git -C fjbms-uniapp diff --check && git -C backend diff --check`：通过。
- [ ] 2026-06-11 Debug 模式真机 UI 复测：待确认普通模式不显示日志入口；Debug 模式 OTA 弹窗显示日志图标，点击后页面级浮层可滚动查看完整升级日志并可复制文本。
- [x] 2026-06-12 后端 4G BMS OTA retained/慢 ACK 诊断单测：新增 `internal/api/app_battery_socket_test.go`，覆盖 BOOT `0x53` 数据包/ACK 解析、慢 ACK 计算和 ACK 后下发间隔计算。
- [x] 2026-06-12 后端定向回归：`cd backend && go test ./internal/api ./internal/service ./router/apps` 通过。
- [x] 2026-06-12 后端 diff 空白检查：`git diff --check -- backend/internal/api/app_battery.go backend/internal/api/app_battery_socket_test.go` 通过。
- [ ] 2026-06-12 生产 OTA 复测：待后端发布后，采集 `bms mqtt socket boot uplink slow ack`、`boot_ack_after_downlink_ms`、`boot_packet_after_ack_ms` 与 APP/BMS 串口日志，确认随机 3~6 秒停顿落点。
- [x] 2026-06-12 4G BMS 休眠唤醒查询补发类型检查：`cd fjbms-uniapp && pnpm exec tsc --noEmit` 通过。
- [x] 2026-06-12 4G BMS 休眠唤醒补发轻量断言：临时编译并执行 `common/lib/bms-protocol/uni-mqtt-socket-transport.wakeup.test.ts`，覆盖读查询可补发、近期有响应不补发、写命令不补发、BOOT OTA 不补发。
- [x] 2026-06-12 UniApp diff 空白检查：`cd fjbms-uniapp && git diff --check` 通过。
- [ ] 2026-06-12 4G BMS 休眠真机复测：待设备休眠 30 秒后进入详情页，确认首个实时读取会出现 `[socket] wakeup resend query` 且第二条查询唤醒后可返回数据。
- [x] 2026-06-12 4G BMS OTA ACK 超时配置断言：临时编译并执行 `common/lib/bms-protocol/boot-ota-runtime-options.test.ts`，确认 MQTT BMS OTA `bootPacketTimeoutMs=3000`，其他阶段超时保持不变。
- [x] 2026-06-12 4G BMS OTA 3 秒 ACK 超时类型检查：`cd fjbms-uniapp && pnpm exec tsc --noEmit` 通过。
- [x] 2026-06-12 4G BMS OTA 3 秒 ACK 超时 diff 空白检查：`cd fjbms-uniapp && git diff --check` 通过。
- [ ] 2026-06-12 4G BMS OTA 真机复测：待使用新包升级真实 4G BMS，确认 `0x53` ACK 未到时约 3 秒触发同包重发，不再等待 20 秒。
- [x] 2026-06-12 生产只读排查 QoS1 后延迟样例：
  - EMQX 目标设备 `360111611350535934373730300A3778` 订阅 `device/socket/rx/360111611350535934373730300A3778` 的 QoS 为 1。
  - 生产后端日志显示 `0x04FA` ACK 于 `2026-06-12 18:20:25.707+08` 到达云端，后端于 `18:20:26.145+08` 下发 `0x04FA` 数据包，随后 `18:20:29.764+08`、`18:20:33.290+08` 重发同包。
  - `bms_bridge_comm_logs` 到 `18:21:30+08` 未查询到 `0x04FB` ACK，判断本次样例不是后端继续下发下一包，而是 `0x04FA` 后未收到下一 ACK。
- [x] 2026-06-12 后端 4G BMS OTA 包序号与 QoS1 日志回归：`cd backend && go test ./internal/api ./internal/bmsbridge` 通过。
- [x] 2026-06-12 后端包序号日志 diff 空白检查：`git -C backend diff --check -- internal/api/app_battery.go internal/bmsbridge/bridge.go internal/bmsbridge/boot_debug.go` 通过。
- [ ] 2026-06-12 发布后生产复测：采集 `boot_packet_seq_hex`、`boot_expected_ack_hex`、`boot_ack_requested_hex`、`boot_ack_for_packet_hex`、`boot_packet_attempt`、`mqtt_message_id` 与 `bms_bridge_comm_logs.parsed_summary`，确认随机延迟发生时 ACK 是否已经离开 BMS/4G 模块。
- [x] 2026-06-12 App Debug OTA 包序号类型检查：`cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false` 通过。
- [x] 2026-06-12 App Debug OTA 包序号 diff 空白检查：`cd fjbms-uniapp && git diff --check -- common/lib/bms-protocol/boot-ota.ts common/lib/bms-protocol/uni-mqtt-socket-transport.ts` 通过。
- [ ] 2026-06-12 App Debug OTA 真机复测：待 Debug 模式下执行 4G BMS OTA，确认日志浮层和复制文本中可见 `packetIndexHex/expectedAckHex/requestedHex/ackForPacketHex`。
- [x] 2026-06-29 生产只读排查目标设备 `360111611350535934373730300A365F`：
  - `telemetry_datas` 与 `bms_bridge_comm_logs` 确认 `2026-06-29 15:39:54.731+08` 有数据入库。
  - 视频测试时段 `16:02~16:06+08` 当前遥测已出现 `packCellSumVoltageV`、单体电压和电流变化，判断小程序未变化不是设备未上报，而是实时读取失败后保留旧状态。
- [x] 2026-06-29 UniApp 4G Socket 响应匹配断言：新增 `uni-mqtt-socket-transport-response-match.test.ts`，覆盖普通 `0x03` 响应按期望 `byteCount` 匹配，以及 `SOCKET_READ=0x0F` 仍按地址区间交集匹配。
- [x] 2026-06-29 UniApp `readRegisters()` 数量校验断言：新增 `client-read-registers.test.ts`，覆盖普通 `0x03` 短响应会抛出数量不匹配，并确认请求会向 Transport 传递期望寄存器数/字节数。
- [x] 2026-06-29 `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`：通过。
- [x] 2026-06-29 临时编译并执行新增协议断言：`client-read-registers.test.ts`、`uni-mqtt-socket-transport-response-match.test.ts` 均通过。
- [x] 2026-06-29 diff 空白检查：FEAT-0049 文档、看板和 UniApp 本次变更文件均通过。
- [ ] 2026-06-29 UniApp 真机复测：待使用包含本次修复的新包进入同一 4G BMS 详情页，确认外部测试改变电压/电流后小程序仪表盘随生产当前遥测或实时读数更新。
- [x] 2026-07-02 生产 MQTT 直连排查目标设备 `36011161145053593437373030124A57`：
  - 高级参数普通 `0x03` 区间 `0x0454/0x0500/0x053A/0x0001/0x0004/0x0030/0x003E` 在无前置超时请求时 0.9~2.5 秒返回。
  - 状态大包 `0x0100 qty=53` 与 `0x0141 qty=79` 也可实时返回；`0x0F 0x0900 qty=36` 两轮无响应，应与高级参数读取隔离。
- [x] 2026-07-02 UniApp 状态轮询取消断言：扩展 `client-read-registers.test.ts`，覆盖 `readAllStatus({ shouldContinue })` 在暂停后不继续排后续状态子请求。
- [x] 2026-07-02 UniApp MQTT 参数读取超时断言：扩展 `client-read-registers.test.ts`，覆盖 `readParamsByKeys(..., { timeoutMs })` 会将短超时传递到 transport。
- [x] 2026-07-02 `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`：通过。
- [x] 2026-07-02 临时编译并执行协议断言：`client-read-registers.test.ts` 通过。
- [ ] 2026-07-02 UniApp 真机复测：待使用新包进入同一 4G BMS `设置 > 高级参数`，确认正常情况下高级参数在数秒内显示，且切页时不会被旧状态轮询拖到约 1 分钟。
- [x] 2026-07-03 UniApp 4G BMS 休眠策略断言：扩展 `uni-mqtt-socket-transport.wakeup.test.ts`，确认默认休眠唤醒阈值为 180 秒，并覆盖从未收到响应/超过阈值才需要主动 probe。
- [x] 2026-07-03 UniApp 参数读取前唤醒 probe 断言：扩展 `client-read-registers.test.ts`，确认 `wakeupReadLink()` 默认发送 `0x0100 qty=1` 轻量读查询、传递短超时，并吞掉休眠超时错误。
- [x] 2026-07-03 `cd fjbms-uniapp && pnpm exec tsc -p tsconfig.json --noEmit --pretty false`：通过。
- [x] 2026-07-03 临时编译并执行协议断言：`client-read-registers.test.ts`、`uni-mqtt-socket-transport.wakeup.test.ts` 均通过。
- [ ] 2026-07-03 UniApp 真机复测：待设备静置超过 3 分钟后进入 `设置 > 高级参数`，确认先触发轻量唤醒读，随后高级参数分组不再因首包休眠无响应长时间空白。
- [x] 2026-07-07 后端 WebSocket/MQTT 普通帧转发日志单测：`cd backend && go test ./internal/api -run 'TestSocket'` 通过；仅出现 macOS SDK `IOMasterPort` 废弃警告。
- [x] 2026-07-07 UniApp MQTT Socket 收包断言：扩展 `uni-mqtt-socket-transport.wakeup.test.ts`，覆盖微信小程序 WebSocket `ArrayBuffer` 与 `Uint8Array` 消息可解码为 JSON `{hex}` 文本。
- [x] 2026-07-07 UniApp 状态轮询超时断言：扩展 `client-read-registers.test.ts`，覆盖 `readAllStatus({ timeoutMs })` 会把 4G 实时轮询短超时传递到 `readSn/head/alarm/tail` 子读取。
- [x] 2026-07-07 临时编译并执行协议断言：`client-read-registers.test.ts`、`uni-mqtt-socket-transport.wakeup.test.ts` 的输出 JS 均通过；单文件 `tsc` 因未加载 uniapp 全局声明出现预期 `Cannot find name 'uni'`，不影响输出断言。
- [x] 2026-07-07 UniApp 项目级类型检查：`cd fjbms-uniapp && ./node_modules/.bin/tsc -p tsconfig.json --noEmit` 通过。
- [x] 2026-07-07 UniApp 参数响应匹配断言：`uni-mqtt-socket-transport-response-match.test.ts` 覆盖现场普通 `0x03` 回包 `7F5501FE030814140B5409603214D464FD` 可满足 `0x040D qty=4` 的 pending 请求。
- [x] 2026-07-07 UniApp 单体参数批量读取断言：`client-read-registers.test.ts` 覆盖单体设置会读取 `0x0400 qty=6` 与 `0x0408 qty=9`，不再把后半段拆成独立 `0x040D qty=4` 请求。
- [x] 2026-07-07 UniApp 参数页失败态检查：MQTT 参数分组首次全空会重试一次；重试后仍全空则不标记分组已加载，用户可重新点击触发真实读取。
- [x] 2026-07-07 MQTTX 导出日志复核：`_resources/fjia.json` 显示 `0x0408 qty=9` 既存在约 172ms 快回包，也存在超过 3 秒才出现且带尾随字节的回包；结合 5 秒单组超时会导致慢窗口下参数分组被误判失败。
- [x] 2026-07-07 UniApp 参数读取超时修正：MQTT 参数分组读取超时从 5 秒调整为 15 秒，避免真实 4G BMS 慢回包触发“打开失败，请重试”。
- [x] 2026-07-07 UniApp Transport 尾随字节断言：`uni-mqtt-socket-transport.wakeup.test.ts` 覆盖 `0x0408 qty=9` 有效帧后拼接 `150C...` 尾随字节时，Transport 仍可解析并返回 9 个寄存器。
- [x] 2026-07-07 UniApp 项目级类型检查：`cd fjbms-uniapp && ./node_modules/.bin/tsc -p tsconfig.json --noEmit` 通过。
- [x] 2026-07-07 UniApp 协议断言执行：项目 tsconfig 编译测试产物后执行 `client-read-registers.test.js`、`uni-mqtt-socket-transport-response-match.test.js`、`uni-mqtt-socket-transport.wakeup.test.js` 均通过。
- [x] 2026-07-07 `fjia2.json` 真实帧回归：新增 `uni-mqtt-socket-transport-fjia2-repro.test.ts`，回放 `0x0100 qty=1`、`0x0400 qty=6`、`0x0408 qty=9` 的真实响应，并在每条真实响应前注入请求 echo，验证 `FrameCollector` 会跳过下行请求帧且单体设置参数可解码。
- [x] 2026-07-07 本轮 UniApp 类型检查：`cd fjbms-uniapp && pnpm exec tsc -p tsconfig.json --noEmit --pretty false` 通过。
- [x] 2026-07-07 本轮协议断言执行：临时编译并执行 `client-read-registers.test.js`、`uni-mqtt-socket-transport-response-match.test.js`、`uni-mqtt-socket-transport.wakeup.test.js`、`uni-mqtt-socket-transport-fjia2-repro.test.js` 均通过。
- [ ] 2026-07-07 UniApp 真机复测：待使用新包停留在 4G BMS `设备详情 > 仪表盘`，通过 MQTTX 订阅 `device/socket/rx/{device_number}` 确认会周期性出现状态读取 payload，并确认 `device/socket/tx/{device_number}` 回包后仪表盘实时刷新。
- [ ] 2026-07-07 UniApp 参数设置真机复测：待使用新包进入 4G BMS `设备详情 > 参数设置 > 单体设置/总压设置`，确认 MQTTX 可见分组读取 payload，慢回包在 15 秒内返回时小程序端可展开并显示参数值。
- [ ] 2026-07-07 生产日志复测：待后端发布后，观察 `/api/v1/app/battery/socket/ws` 普通帧日志是否连续出现 `ws_to_mqtt_rx` 与 `mqtt_tx_to_ws`，并用 `ws_write_ms/mqtt_publish_wait_ms` 排除 Broker/WS 转发阻塞。
- [x] 2026-07-07 后端 4G 设备类型判定单测：`isFourGBatteryDetail()` 覆盖 BLE-only、4G、蓝牙+4G 与 `comm_chip_id` 兜底。
- [x] 2026-07-07 后端定向回归：`cd backend && go test ./internal/api ./internal/service -run 'TestSocket|TestIsFourGBatteryDetail|TestNormalizeAppBattery|TestMergeCurrentTelemetry' -count=1` 通过，仅有 macOS SDK `IOMasterPort` 废弃警告。
- [x] 2026-07-07 代码空白检查：`git -C backend diff --check -- internal/api/app_battery.go internal/service/app_battery.go internal/service/app_battery_report_test.go` 与 `git -C fjbms-uniapp diff --check -- pages/device-battery/useBatteryDetail.ts` 通过。
- [ ] 2026-07-07 4G 在线状态生产复测：待发布后，使用当前无主动上报但可实时读数的 4G 设备进入详情页，确认 `device/socket/tx/{device_number}` 回包后 `devices.is_online=1`，移动端顶部从 4G 离线切换为 4G 在线。
- [x] 2026-07-10 UniApp 项目级类型检查：`cd fjbms-uniapp && pnpm exec tsc -p tsconfig.json --noEmit --pretty false` 通过。
- [x] 2026-07-10 移动端数据仲裁断言：临时 CommonJS 编译并执行 `detail-data-arbiter.test.ts` 通过，覆盖 bootstrap/fallback 迟到、实时恢复、A 设备响应晚到 B 会话、云端 `last_report_ts` 倒退、fallback 早于 last-good realtime、单次实时失败不回退和无实时首帧可快速预填。
- [x] 2026-07-10 后端 P0 定向回归：`cd backend && go test ./internal/adapter/mqttadapter ./internal/bmsbridge ./internal/storage ./internal/uplink ./internal/api ./cmd/bms-bridge` 通过；仅出现 macOS SDK `IOMasterPort` 既有废弃警告。
- [x] 2026-07-10 后端竞态回归：`cd backend && go test -race ./internal/adapter/mqttadapter ./internal/bmsbridge ./internal/storage ./internal/uplink ./internal/api ./internal/service` 通过；仅有既有 macOS 链接/废弃警告。
- [x] 2026-07-10 后端单测覆盖：主 MQTT adapter 默认投递与普通设备 storage 时间语义不变、bridge 独立 clean/ordered 配置、retained 丢弃、原始 Topic 分片 FIFO、同设备严格递增毫秒、远未来时间回退、current 时间单调 upsert、fallback 多历史行映射。
- [x] 2026-07-10 快照新鲜度断言：覆盖 `snapshot_ts == last_report_ts` 可使用完整快照、快照早于任一 current 最新时间或缺少自身时间时改用逐 key current。
- [x] 2026-07-10 后端快照合并回归：覆盖比快照旧的单键 current 不得反向覆盖新快照，同时比快照新的单键仍可覆盖。
- [ ] 2026-07-10 真机弱网回归：待使用包含本次修复的新包，在仪表盘/电芯页制造一次短暂读超时，确认页面保留最后实时值且不闪回旧快照；连续失败超过保护窗口后才进入云端兜底，实时恢复后立即切回。
- [ ] 2026-07-10 发布后数据链路观察：确认 retained 上行记录为 `uplink_ignored`，同一设备当前遥测 `ts` 不倒退，并观察 bridge 分片队列无持续满载告警。
- [x] 2026-07-20 UniApp 项目级类型检查：`cd fjbms-uniapp && pnpm exec tsc -p tsconfig.json --noEmit --pretty false` 通过。
- [x] 2026-07-20 参数/历史页轮询策略断言：临时 CommonJS 编译并执行 `detail-polling-policy.test.ts` 通过，覆盖 MQTT 仪表盘正常轮询、MQTT 参数页和历史记录页 30 秒间隔与首轮 30 秒延时、BLE 参数页和历史记录页暂停，以及连接未就绪暂停。
- [x] 2026-07-20 代码与文档空白检查：FEAT-0049 文档及本次 UniApp 文件 `git diff --check` 通过。
- [ ] 2026-07-20 历史记录页真机保活复测：进入 4G BMS `设备详情 > 历史记录` 静置超过 3 分钟，通过 MQTTX 确认约每 30 秒出现一次状态读取及设备回包，顶部状态保持 4G 在线且设备不进入休眠。
- 说明：原 2026-07-20 参数页 30 秒真机验收项已被 2026-08-21 参数页 10 秒验收项替代，不再按旧周期执行。
- [ ] 2026-07-20 历史读取并行场景复测：在历史记录页保活期间切换保护次数/状态记录并加载更多，确认 30 秒状态读取只在串行队列中等待，不阻塞或污染 `0x4C/0x4D` 历史响应。
- [x] 2026-07-20 Web 电芯无效值回归：`cd frontend && pnpm exec tsx --test src/views/device/details/modules/bms-panel/cell-voltage.test.ts` 通过 4/4，覆盖全 `65535` 实时数组回退有效云端数组、实时/云端均无效时为空、部分无效项保序显示和字符串数值归一化。
- [x] 2026-07-20 Web 定向 ESLint：`cd frontend && pnpm exec eslint src/views/device/details/modules/bms-panel/index.vue src/views/device/details/modules/bms-panel/cell-voltage.ts src/views/device/details/modules/bms-panel/cell-voltage.test.ts` 通过。
- [x] 2026-07-20 Web 项目级类型检查：`cd frontend && pnpm typecheck` 通过。
- [x] 2026-07-20 Web 生产构建：`cd frontend && pnpm build` 通过；仅输出项目既有的 `GridV2`、`ContextMenu` 自动组件命名冲突提示。
- [ ] 2026-07-20 Web 浏览器现场复测：进入截图所示 4G BMS 设备详情电芯页，确认不再显示 `65.535 V`；若云端存在有效电芯数组则回退显示真实值，否则展示“暂无电芯数据”。
- [x] 2026-07-25 后端主动读取快照定向回归：`cd backend && go test ./internal/service ./internal/api ./router/apps -count=1` 通过；覆盖 Socket owner 的设备/会话/用户/租户/有效期匹配、主动快照与普通 current 隔离、服务端时间单调 upsert，只有 macOS SDK `IOMasterPort` 既有废弃警告。
- [x] 2026-07-25 UniApp 项目级类型检查：`cd fjbms-uniapp && pnpm exec tsc -p tsconfig.json --noEmit --pretty false` 通过。
- [x] 2026-07-25 UniApp 策略与 Transport 断言：临时 CommonJS 编译并执行 `detail-data-arbiter.test.ts`、`detail-polling-policy.test.ts`、`instrument-passthrough-policy.test.ts`、`uni-mqtt-socket-transport.wakeup.test.ts`，全部通过；覆盖主动读取快照优先级、无快照兼容 fallback、Socket `session_id` 获取/断开清理，以及既有轮询和仪表 10 秒等待策略。
- [ ] 2026-07-25 后端全量 `go test ./...`：本功能相关包通过；仓库既有环境型测试未通过，`initialize/test.TestSetDevice` 因测试缓存未初始化产生 nil pointer，`project/test.TestDatebase` 因未设置 `run_env`/测试数据库先报“未知环境”后产生 nil pointer，均未进入本功能代码路径。
- [ ] 2026-07-25 4G 真机与发布后验收：待在微信小程序、iOS、Android 使用真实设备确认在线交互成功后写入主动快照；随后使设备离线，确认 fallback 显示该快照；读取失败、HTTP 失败、Socket occupied、退出/换账号和旧会话迟到提交不得覆盖；无主动快照设备继续显示原主动上报数据。
- [x] 2026-08-21 UniApp 项目级类型检查：`cd fjbms-uniapp && pnpm exec tsc -p tsconfig.json --noEmit --pretty false` 通过。
- [x] 2026-08-21 扫码在线策略断言：临时 CommonJS 编译并执行 `scan-four-g-online-policy.test.ts` 通过，覆盖非扫码不启用、立即在线、60 秒边界、有效回包续期、超时后恢复和跨 session 拒绝。
- [x] 2026-08-21 路由与 Transport 断言：`scan-routing.test.js` 通过扫码直达、UUID 绑定和 BLE 配网来源透传；`uni-mqtt-socket-transport.wakeup.test.ts` 通过，确认意外有效帧不触发回调、匹配当前请求的有效帧只触发一次。
- [x] 2026-08-21 参数页保活策略断言：执行 `pnpm dlx tsx pages/device-battery/detail-polling-policy.test.ts` 通过，覆盖 4G MQTT 参数页首轮及后续间隔均为 10 秒且小于 15 秒休眠阈值、历史页保持 30 秒、BLE 参数/历史页及连接未就绪状态继续暂停。
- [x] 2026-08-21 参数页保活静态回归：UniApp TypeScript 检查、设备详情 Vue SFC 编译及子仓空白检查通过；策略继续复用原串行 `readAllStatus()` 生命周期，没有新增并发读取循环。
- [ ] 2026-08-21 微信小程序真机/MQTTX 验收：扫码进入后确认顶部立即在线且后台持续下发；完全无回包时约 60 秒转离线，第 55 秒返回匹配帧时保持在线。
- [ ] 2026-08-21 参数页真机/MQTTX 验收：进入 4G BMS `设备详情 > 参数设置` 后不操作并静置至少 1 分钟，确认约每 10 秒出现一轮状态读取且持续有有效回包，设备不在 15 秒进入休眠；在保活临界点展开参数分组并执行一次写入，确认所有指令串行且响应不串包。
- [ ] 2026-08-21 Android/iOS 回归：确认公共详情逻辑、BLE-only 设备、4G 参数页 10 秒保活及历史页 30 秒串行保活无行为回退。
- [x] 2026-08-28 OTA 900ms策略断言：`pnpm dlx tsx common/lib/bms-protocol/boot-ota-runtime-options.test.ts` 通过，确认BLE与MQTT/4G共享的 `0x50`～`0x53` 应答窗口为900ms，超时后220ms重发缓冲及 `0x54` 策略未变。
- [x] 2026-08-28 OTA 时序与类型检查：`pnpm dlx tsx common/lib/bms-protocol/boot-ota-timing.test.ts`、`pnpm exec tsc --noEmit --pretty false` 通过。
- [ ] 2026-08-28 真机成功率验证：待微信小程序Android、iOS、BLE BMS/仪表及4G/MQTT BMS使用同一固件多轮升级，记录失败百分比、包序号、ACK RTT与重发次数。
- [x] 2026-09-02 OTA 600ms策略断言：`pnpm dlx tsx common/lib/bms-protocol/boot-ota-runtime-options.test.ts` 通过，确认BLE与MQTT/4G共享的 `0x50`～`0x53` 应答窗口为600ms，超时后220ms重发缓冲及 `0x54` 策略未变。
- [x] 2026-09-02 OTA 450ms策略断言：临时编译执行 `boot-ota-runtime-options.test.ts` 与 `boot-ota-timing.test.ts` 通过，确认BLE与MQTT/4G共享应答窗口为450ms、重发等待220ms、总节拍670ms，`0x54` 策略未变。
- [ ] 2026-09-02 MQTT/4G冒烟回归：使用真实设备完成一次升级，确认450ms窗口下数据包ACK、重发及升级后版本变化。
- [ ] 2026-09-02 真机成功率验证：待微信小程序Android、鸿蒙、iOS、BLE BMS/仪表及4G/MQTT BMS使用同一固件多轮升级，记录失败百分比、包序号、ACK RTT与重发次数。
- [x] 2026-08-30 扫码 handoff 来源断言：`pnpm dlx tsx common/device-provision/detail-handoff.test.ts` 通过，覆盖扫码来源随 handoff 保存/消费、消费后不残留及手动配网不误标为扫码。
- [x] 2026-08-30 扫码在线定向回归：`scan-four-g-online-policy.test.ts`、`scan-routing.test.js` 与 UniApp 项目级 TypeScript 检查通过；普通详情、BLE-only、60 秒边界和扫码各级路由语义保持不变。
- [x] 2026-08-30 小程序编译与轮询回归：详情/配网页 SFC script 编译、MQTT Transport 匹配回包断言、详情轮询策略及 HBuilderX 5.24 微信小程序编译通过；编译仅提示项目未配置 uniCloud 服务空间，不影响本地小程序产物生成。
- [ ] 2026-08-30 微信小程序真机/MQTTX 验收：分别覆盖已绑定设备直达、UUID 绑定后跳转、扫码 BLE 配网 handoff 三条路径；确认进入 4G 仪表盘即显示在线、无有效回包约 60 秒转离线、有效回包续期。
- [x] 2026-09-02 首页在线宽限定向回归：详情来源断言、首页/组织列表路由静态断言、60 秒策略、扫码路由、MQTT Transport 匹配回包断言及 UniApp 项目级 TypeScript 检查通过；首页来源启用宽限，组织列表、手动 BLE 搜索和未标记入口保持原行为。
- [ ] 2026-09-02 首页入口真机/MQTTX 验收：从首页列表进入离线 4G/4G+BLE 设备详情后立即显示“4G 在线”，无匹配有效回包约 60 秒转离线；组织设备列表进入仍直接按后端状态显示，BLE-only 行为不变。

## 2026-09-03 OTA定向回归

本节是本日前轮“同包重发”方案的本地验证历史；下一节是随后执行但已撤销的超时推进试验，现行策略见2026-09-04回归门槛。通过仅代表本地自动化结果；前轮共享清单见 [FEAT-0046测试报告](../FEAT-0046-meter-ota-packages-and-uniapp-flow/03-test-report.md#4-2026-09-03-本轮本地验证)。

- [x] `pnpm dlx tsx common/lib/bms-protocol/boot-ota-transport.test.ts`：使用实际MQTT Socket transport的connect/onMessage链路模拟，449/500/669ms ACK均被同一请求接收；无ACK时本轮约672ms重发，旧ACK不推进或回退。覆盖纯hex/JSON消息、混合普通/坏帧、分段ACK、完成阶段旧ACK和空ACK拒绝、普通请求取消/排队拒绝/结束恢复。
- [x] `pnpm dlx tsx common/lib/bms-protocol/boot-ota-runtime-options.test.ts` 与 `pnpm dlx tsx common/lib/bms-protocol/boot-ota-timing.test.ts`：450ms+220ms、ACK后进度、有界恢复、设备指定包长和严格完成条件通过，4G仍单发 `0x54`、5秒窗口。
- [x] `pnpm dlx tsx pages/device-battery/ota-session.test.js` 与 `pnpm dlx tsx pages/device-battery/detail-polling-policy.test.ts`：执行实际页面函数和Vue批量watch，cloud/instrument及BLE/MQTT会话OTA时均暂停轮询，成功/失败后恢复，4G参数页恢复10秒保活；屏幕保护与独占清理通过。
- [x] 普通通讯回归：`pnpm dlx tsx common/lib/bms-protocol/uni-mqtt-socket-transport-response-match.test.ts`、`pnpm dlx tsx common/lib/bms-protocol/uni-mqtt-socket-transport.wakeup.test.ts`、`pnpm dlx tsx common/lib/bms-protocol/uni-mqtt-socket-transport-fjia2-repro.test.ts` 均通过。
- [x] `pnpm exec tsc --noEmit --pretty false`，以及已安装 `@vue/compiler-sfc` 对详情/参数页script/template编译通过。
- [ ] Android微信小程序与App各连续20次真实4G升级，至少一次弱网，核对升级后版本；同时观察OTA中无普通查询、结束后10秒保活恢复，记录包序号、ACK RTT及重发。真实蜂窝延迟超过670ms仍可能触发重试。
- [ ] iOS 4G完整升级冒烟、现场MQTTX/后端日志联调；本轮未执行后端/管理端构建、HBuilderX打包或发布，硬件验收前保持 `in_progress`。

## 2026-09-03 客户超时推进试验

当时执行的完整13项本地回归与命令见 [FEAT-0046历史试验报告](../FEAT-0046-meter-ota-packages-and-uniapp-flow/03-test-report.md#5-2026-09-03-客户超时推进试验)。

- [x] 实际MQTT transport接模拟Socket，首/中/末包无ACK分别约671/670/672ms后推进下一包，不原包重发；收到设备补包请求可回退恢复，超时不伪造确认进度。
- [x] 所有数据ACK缺失时仍尝试最终真实CRC32校验，`0x54` 超时与非零状态均失败，仅真实 `status=0` 成功；迟到/重复ACK、分段/坏帧、独占清理与普通通讯回归通过。
- [x] MQTT数据最小帧间隔、包间/4KB等待均0，准备ACK后立即首包；单发5s完成窗口不变。日志内存缓冲、手动复制、结束保存和页面finally恢复验证通过。
- [x] 13项脚本、TypeScript与详情/参数SFC编译通过；未执行后端、数据库、协议或依赖变更。
- [ ] Android微信小程序/App各连续20次4G升级、每组至少一次弱网与版本变化，iOS冒烟及MQTTX/后端联调待验收；超时推进可能最终CRC失败，不据本地模拟承诺成功率。未提交、推送、打包或部署，保持 `in_progress`。

## 2026-09-04 4G OTA最新回归门槛

本节取代上一节的超时推进策略；上一节仅作为已执行但已撤销的试验记录。共享失败证据与完整测试矩阵见 [FEAT-0046测试报告](../FEAT-0046-meter-ota-packages-and-uniapp-flow/03-test-report.md#6-2026-09-04-页边界失败复盘与最新验收)。

- [x] MQTT实际transport模拟首/中/末包ACK缺失，断言约670ms后发送相同序号和载荷，未收到合法 `requested` 前不改变发送游标、确认进度或UI进度；同包达到有界上限后明确失败。
- [x] 覆盖设备 `requested` 正常前进、重复、回退、`status=3`纠正、非法范围及反复无进展，断言下一包唯一由合法设备游标决定，不能因MQTT发布成功或ACK超时自行递增。
- [x] 覆盖64/128/256/512/1024字节包档位的4KB边界，断言确认整页后等待300ms再发下一页首包；同一页首包重试不重复等待，设备回退后重新跨越边界会再次保护；BLE与MQTT/4G均为 `minFrameIntervalMs=0`、`packetDelayMs=0`，普通包仍由ACK驱动且无额外固定等待。
- [x] 覆盖末包ACK缺失，断言不得发送 `0x54`；确认 `requested == packetTotal` 后才等待300ms发送真实CRC32完成帧。`0x54 status=0`成功，非零、超时、Socket断连均失败，不能复用BLE完成后断连兼容。
- [x] 验证OTA独占期间无普通状态读取和休眠唤醒补发插入，WebSocket ping保持；成功、失败、取消后释放独占并按当前Tab恢复10秒参数保活或其他轮询。
- [x] 验证1585个 `0x53` 数据包保留1585条紧凑结构化 ACK，每条含 `seq/status/requested/RTT`；Boot 层不重复记录 `0x53` 完整十六进制，transport 层完整十六进制只保留首包、末包、4KB边界包、同包重试和异常；会话头未因包数丢失，手动复制和finally集中保存可用。
- [x] 已执行共享Boot时序/运行参数/BLE与MQTT实际transport、普通响应匹配、wakeup、fjia2样例、OTA页面会话、轮询策略、日志精简、TypeScript与详情/参数SFC编译及 `git diff --check`；全部通过。
- [ ] 真机门槛：Android微信小程序和App各连续成功20次4G BMS OTA，每组至少一次弱网并核对升级后版本；同步采集App、MQTTX/后端与硬件串口的序号/页边界/ACK RTT/重试证据。iOS 4G至少一次完整冒烟；全部完成前保持 `in_progress`。

## 2026-09-04 Android BLE修复的4G回归边界

- [x] 已确认BLE响应写、原生回调与450ms读取探测未进入MQTT transport；4G运行参数仍为450+220ms、同序重发、300ms页保护和单发5秒完成窗口。
- [x] 已执行MQTT实际transport、Boot运行参数/时序、普通响应、wakeup、fjia2及页面OTA会话回归；全部通过。
- [ ] 真机门槛不变：Android微信小程序/App各20次4G OTA、至少一次弱网并核对版本，iOS 4G至少一次完整冒烟；未完成前保持 `in_progress`。
