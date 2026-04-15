# FEAT-0041 UniApp OTA 地址口径统一与仪表会话升级支持 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-15
- related_feature: FEAT-0041
- version: v0.1.0

## 1. 实施记录
1. 排查 UniApp OTA 入口与 Boot 协议链路，确认当前 Boot 升级主流程已区分仪表/ BMS，但查询地址未严格统一。
2. 确认 OTA 入口在仪表临时会话下被 `allowOta` 直接禁用。
3. 确认后端 OTA 检查接口当前强制要求 `device_id`，导致仪表临时会话无法匹配升级包。
4. 已完成 UniApp OTA 入口调整：
   - `detail.vue` 放开仪表临时会话下 OTA 可用条件
   - 仪表会话也允许自动 OTA 检查
5. 已完成 UniApp OTA 地址口径统一：
   - 仪表 Boot 查询/升级固定 `0xFC`
   - BMS Boot 查询/升级固定 `0x01`
6. 已完成后端 OTA 检查接口兼容：
   - `device_id` 改为可选
   - 无 `device_id` 时按 `model + version` 匹配升级包
7. 已完成定向静态校验：
   - `cd backend && go test ./internal/service/...`
   - `cd fjbms-uniapp && pnpm exec tsc --noEmit`

## 2. 待执行项
- 真机验证仪表 / BMS 两类 OTA 行为。

## 3. 当前状态
- 代码修改和静态校验已完成，当前待运行态验收。
