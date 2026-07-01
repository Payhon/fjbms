# FEAT-0041 UniApp OTA 地址口径统一与仪表会话升级支持 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-06-30
- related_feature: FEAT-0041
- version: v0.3.0

## 1. 背景与目标
- 背景：
  - 当前 UniApp 设备详情页 OTA 升级虽然已在协议层区分仪表和 BMS，但地址口径并不严格一致。
  - Boot 查询 `0x50` 对 BMS 当前走的是 `0x00`，不符合“BMS 固定 `0x01`、仪表固定 `0xFC`”的要求。
  - 仪表临时会话下 OTA 入口当前被禁用，且 OTA 检查接口要求 `device_id`，导致仪表会话无法完成升级链路。
  - 仪表设备存在蓝牙透传下方 BMS 板和有线连接下方 BMS 板两类；有线仪表在蓝牙连接仪表后可直接读到 BMS 状态，但当前详情页仍展示“仪表临时连接”浮动提示，引导用户继续扫码绑定 BMS，容易造成误操作。
  - 有线仪表下方未接入 BMS 板时，当前页面会持续停留在“正在读取 BMS 实时数据”遮罩，用户无法回到主面板，也看不到继续扫码绑定 BMS 的入口。
- 目标：
  1. OTA Boot 查询与升级全流程严格按设备类型使用固定目标地址。
  2. 启用仪表临时会话下的 OTA 入口和升级流程。
  3. 后端 OTA 检查支持无 `device_id` 的仪表会话，允许按 `model + version` 匹配升级包。
  4. 仪表临时会话下，若已能读取到 BMS 状态，判定为仪表已连接下方 BMS 板，不再展示继续扫码绑定 BMS 的浮动提示。
  5. 仪表临时会话连续 3 次未读取到 BMS 状态时，回到设备详情主面板，并展示包含有线仪表检查建议和继续扫码入口的提示。
- 备注：
  - 2026-04-21 起，仪表 OTA 的升级包管理与手动选包升级流程由 FEAT-0046 继续演进；FEAT-0041 保留地址口径统一与会话能力的基础记录。

## 2. 范围
### In Scope
- `fjbms-uniapp/pages/device-battery/detail.vue` OTA 可用条件与自动检查逻辑调整。
- `fjbms-uniapp/pages/device-battery/components/params-tab.vue` OTA 启动逻辑调整。
- `fjbms-uniapp/service/app-battery.ts` OTA 检查请求类型调整。
- `backend/internal/model/app_battery.http.go` OTA 检查请求结构调整。
- `backend/internal/service/app_battery.go` OTA 检查支持无 `device_id` 的模型匹配分支。
- `fjbms-uniapp/pages/device-battery/useBatteryDetail.ts` 仪表无透传/无 BMS 状态识别与状态暴露。
- `fjbms-uniapp/pages/device-battery/detail.vue` 仪表临时连接浮动提示显隐条件调整。
- `fjbms-uniapp/lang/zh-CN.ts`、`fjbms-uniapp/lang/en-US.ts` 仪表临时连接提示文案调整。
- FEAT-0041 文档和看板同步更新。

### Out of Scope
- 不改 OTA 包管理后台页面。
- 不改 Boot OTA 分包、重试、CRC 校验机制。
- 不调整 BLE 会话模型本身。

## 3. 用户价值
- 仪表连接场景下可直接在移动端执行 OTA 升级。
- OTA 地址口径统一后，协议行为更可预期，减少因目标地址不一致导致的升级失败。

## 4. 验收标准
1. 仪表 OTA 的 Boot 查询和升级指令固定使用目标地址 `0xFC`。
2. BMS OTA 的 Boot 查询和升级指令固定使用目标地址 `0x01`。
3. 仪表临时会话下设备详情页可看到并点击 OTA 升级入口。
4. 仪表临时会话下，即使 `device_id` 为空，也可基于 `model + version` 完成 OTA 检查。
5. 仪表临时会话首帧 BMS 状态读取成功后，不展示“仪表临时连接”浮动提示和顶部收起后的仪表入口。
6. 仪表临时会话连续 3 次读取 BMS 状态超时或无响应后，不再停留在“正在读取 BMS 实时数据”遮罩，改为展示设备详情主面板。
7. 仪表临时会话无法读取下方 BMS 状态时，仍可展示继续扫码绑定 BMS 的提示，且文案提示有线仪表检查 BMS 板连接和供电。
8. 本次改动不会引入 UniApp TypeScript 编译错误或后端编译错误。

## 5. 风险与约束
- 仪表临时会话没有平台侧 `device_id`，升级包匹配只能依赖 `model + version`，因此模型名必须和后台 `battery_models.name` 对齐。
- 若存在同租户同名模型映射到多个配置，当前仍沿用“命中首个模型配置”的既有策略。
- 详情页只能在首帧读取完成后判断是否已连下方 BMS；为避免有线仪表首帧读取期间误弹提示，读取中先不展示扫码浮动提示。
- 当前无法通过寄存器区分蓝牙仪表是有线还是无线，因此提示文案统一覆盖有线检查和扫码绑定两种处理方式。

## 6. 回滚方案
- 回滚 UniApp OTA 可用条件和目标地址选择逻辑。
- 回滚 `useBatteryDetail.ts` 仪表无透传状态暴露和 `detail.vue` 仪表浮动提示显隐条件，恢复为进入仪表会话后按 `allow_scan_handoff` 展示。
- 回滚中英文仪表临时连接提示文案。
- 回滚后端 OTA 检查对无 `device_id` 的兼容逻辑。
- 回滚 FEAT-0041 文档和看板状态。
