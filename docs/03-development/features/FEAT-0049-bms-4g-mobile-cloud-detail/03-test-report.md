# FEAT-0049 BMS 4G 移动端云端详情链路 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-27
- related_feature: FEAT-0049
- version: v0.1.0

## 测试用例
- 后端：当前遥测接口可通过已绑定/组织可见设备查询数据。
- 后端：无 `bms.snapshot` 时仍返回当前摘要遥测 map。
- UniApp：4G-only 设备进入详情页不发起 BLE 连接，不因主动连接失败显示离线。
- UniApp：有当前遥测但无 `cell.voltagesMv` 时，仪表盘有摘要数据，电芯 Tab 显示明确空态。

## 当前结果
- [x] `go test ./internal/bmsbridge ./internal/bms/protocol ./internal/bms/status ./internal/service`：通过。
  - 覆盖用户提供的 `0x0141` 上报帧，解析出 14 路单体电压、4 路电芯温度。
  - 校验最高电压 `3002mV`、最低电压 `2973mV`、压差 `29mV`、单体和 `41.816V`。
  - 温度寄存器按当前协议实现公式 `raw - 2731` 后除以 10，结果为 `27.0/28.0/27.0/27.0°C`。
- [x] `cd frontend && pnpm build`：通过；构建期间存在既有 `eval` 与 unocss 图标加载警告，不影响本次构建结果。
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
- [ ] `go test ./...`：失败在既有环境依赖用例，非本次改动包；`initialize/test` 空指针，`backend/test` 未设置 `run_env` 导致 DB 为空。
