# FEAT-0041 UniApp OTA 地址口径统一与仪表会话升级支持 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-04-15
- related_feature: FEAT-0041
- version: v0.1.0

## 1. 背景与目标
- 背景：
  - 当前 UniApp 设备详情页 OTA 升级虽然已在协议层区分仪表和 BMS，但地址口径并不严格一致。
  - Boot 查询 `0x50` 对 BMS 当前走的是 `0x00`，不符合“BMS 固定 `0x01`、仪表固定 `0xFC`”的要求。
  - 仪表临时会话下 OTA 入口当前被禁用，且 OTA 检查接口要求 `device_id`，导致仪表会话无法完成升级链路。
- 目标：
  1. OTA Boot 查询与升级全流程严格按设备类型使用固定目标地址。
  2. 启用仪表临时会话下的 OTA 入口和升级流程。
  3. 后端 OTA 检查支持无 `device_id` 的仪表会话，允许按 `model + version` 匹配升级包。
- 备注：
  - 2026-04-21 起，仪表 OTA 的升级包管理与手动选包升级流程由 FEAT-0046 继续演进；FEAT-0041 保留地址口径统一与会话能力的基础记录。

## 2. 范围
### In Scope
- `fjbms-uniapp/pages/device-battery/detail.vue` OTA 可用条件与自动检查逻辑调整。
- `fjbms-uniapp/pages/device-battery/components/params-tab.vue` OTA 启动逻辑调整。
- `fjbms-uniapp/service/app-battery.ts` OTA 检查请求类型调整。
- `backend/internal/model/app_battery.http.go` OTA 检查请求结构调整。
- `backend/internal/service/app_battery.go` OTA 检查支持无 `device_id` 的模型匹配分支。
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
5. 本次改动不会引入 UniApp TypeScript 编译错误或后端编译错误。

## 5. 风险与约束
- 仪表临时会话没有平台侧 `device_id`，升级包匹配只能依赖 `model + version`，因此模型名必须和后台 `battery_models.name` 对齐。
- 若存在同租户同名模型映射到多个配置，当前仍沿用“命中首个模型配置”的既有策略。

## 6. 回滚方案
- 回滚 UniApp OTA 可用条件和目标地址选择逻辑。
- 回滚后端 OTA 检查对无 `device_id` 的兼容逻辑。
- 回滚 FEAT-0041 文档和看板状态。
