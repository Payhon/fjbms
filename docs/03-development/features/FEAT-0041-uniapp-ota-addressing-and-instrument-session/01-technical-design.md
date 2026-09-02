# FEAT-0041 UniApp OTA 地址口径统一与仪表会话升级支持 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-08-31
- related_feature: FEAT-0041
- version: v0.5.0

## 1. 方案概览
- UniApp OTA 地址统一：
  - 仪表：Boot 查询 `0x50`、进入 `0x51`、准备 `0x52`、分包 `0x53`、完成 `0x54` 全部使用 `0xFC`
  - BMS：上述全部命令统一使用 `0x01`
- 仪表会话 OTA 放开：
  - 取消 `sessionMode === 'instrument'` 对 OTA 的禁用条件。
  - 自动 OTA 检查在仪表会话下也允许触发。
- 后端 OTA 检查兼容：
  - `device_id` 改为可选。
  - 有 `device_id` 时继续走现有绑定校验和设备配置映射。
  - 无 `device_id` 时直接按 `model` 反查 `battery_models -> device_config_id`，再匹配 OTA 包。
- 仪表扫码提示显隐：
  - 仪表临时会话下，`readAllStatus()` 成功后 `status.value` 存在，视为已能读取下方 BMS 状态。
  - `useBatteryDetail` 将现有 `instrumentPassthroughUnavailable` 返回给详情页；该状态由独立的 10 秒仪表首帧等待截止时间控制，不再由连续失败次数决定。
  - “仪表临时连接”浮动提示仅在仪表会话允许扫码交接、当前蓝牙已连接、未连接中、未读取到 BMS 状态，且不处于首帧读取等待中或已确认无 BMS 状态时展示。
  - 首帧成功后自动收起浮动提示，顶部入口按 FEAT-0052 保留。到期仍无状态时隐藏 loading、展示等待 BMS 提示，保持蓝牙连接与串行轮询。
  - 截止时间捕获当前会话和轮询代次；10 秒到期仅更新 UI 标志，不递增轮询代次，因此同会话完整迟到数据可更新，已取消/已切换会话的旧结果仍由代次校验丢弃。
  - 读取成功、新会话、断开、页面销毁、人工重新读取和重新连接时清除旧计时器；人工操作重新获得完整 10 秒窗口。
- 补充：
  - FEAT-0046 已将“仪表升级包管理 + UniApp 手动选包升级”从本功能中拆出，当前文档主要描述地址口径与仪表会话 OTA 能力基础。

## 2. 关键流程
1. 设备详情页进入仪表临时会话。
2. OTA 检查按 `model + version` 请求 `/api/v1/app/battery/ota/check`。
3. 后端根据模型找到 `device_config_id`，返回是否需要升级及固件下载地址。
4. 前端点击升级后，按设备类型选择固定 Boot 目标地址：
   - 仪表 `0xFC`
   - BMS `0x01`
5. `bootOtaUpgrade()` 全流程按该地址下发 Boot 命令。
6. 详情页仪表会话进入后先发起 BMS 状态读取：
   - 读取中不展示扫码提示，避免有线仪表首屏误引导。
   - 读取成功后展示正常仪表盘数据，不展示扫码提示。
   - 10 秒截止时间到期仍无有效状态时，关闭 loading、展示等待提示和扫码入口；轮间等待由 1.2 秒调整为 3 秒，成功后恢复 2 秒。

### 2026-08-31 持续查询与扫码恢复
- `instrumentPassthroughUnavailable` 保留为兼容 UI 标志，语义为首帧等待超时，不再作为 `startPolling`、`resumePolling` 或后续调度的终止条件。
- 扫码有效且当前客户端仍有效时，暂停并失效旧轮询、清空 BMS 状态和首帧计时，进入配置独占状态。二维码取消或非法不触碰原数据。
- 配置 ACK 与配置超时均走一次现有断开重连；超时仅提示结果待确认。重连等待保留 450ms，页面销毁/操作取消会结束等待且不得继续连接。
- `loadInstrumentSession` 等待实际 `connectAuto` 完成。扫码流程结束时释放配置独占，明确应用当前 Tab 策略；连接失败则保持离线，不无限重连。
- 仪表配置/OTA 独占和页面销毁时，Tab/连接 watcher 不得抢先恢复查询。参数/历史 Tab 暂停、原 Transport 串行队列和 `0xFC` 配置地址不变。
- 本次不修改对外接口、协议、数据库或普通 BMS/MQTT 策略；内部增加清空仪表 BMS 状态的入口，保留会话/客户端/轮询代次保护。

## 3. 测试策略
- `cd fjbms-uniapp && pnpm exec tsc --noEmit`
- `cd fjbms-uniapp && git diff --check -- pages/device-battery/detail.vue pages/device-battery/useBatteryDetail.ts lang/zh-CN.ts lang/en-US.ts`
- `cd backend && go test ./internal/service/...`
- 手工验证：
  - BMS 详情页 OTA 查询和升级
  - 仪表临时会话 OTA 查询和升级
  - 查询请求日志中目标地址是否按设备类型固定
  - 有线仪表未接 BMS 时约 10 秒后返回主面板并显示扫码提示
  - 10 秒内成功回包、临界回包、迟到回包、人工重试和会话切换

## 4. 兼容性与迁移
- 不涉及数据库迁移。
- 既有基于 `device_id` 的 BMS OTA 检查链路保持兼容。
- 不修改 BLE Transport 的单请求超时、备用写重试和串行队列语义。
