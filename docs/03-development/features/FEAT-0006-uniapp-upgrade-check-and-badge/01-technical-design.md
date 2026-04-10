# FEAT-0006 UniApp 升级检测与提示体验优化 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-10
- related_feature: FEAT-0006
- version: v0.1.0

## 1. 方案概览
- 在 `pages/device-battery/detail.vue` 上提页面级 OTA 状态，统一管理自动检测结果与红点显隐。
- 自动检测仅在云端设备详情页、默认仪表盘标签页、且已拿到 `device_id + model + version` 时发起。
- `params-tab.vue` 改为消费父级透传的 OTA 状态；手动点击 OTA 行时优先使用共享结果，缺失时再兜底请求。

## 2. 接口与数据结构
- 继续沿用 `POST /api/v1/app/battery/ota/check`。
- 页面内新增 `DeviceOtaCheckState`：
  - `checking`
  - `checked`
  - `needUpgrade`
  - `targetVersion`
  - `firmwareUrl`
  - `lastCheckedVersion`
  - `errorMessage`
- `params-tab.vue` 新增 props：
  - `otaInfo`
  - `otaChecking`
  - `otaNeedUpgrade`

## 3. 关键流程
- 自动检测流程
  - `detail.vue` 监听 `activeTab / sessionMode / battery / status` 关键字段。
  - 当 `activeTab===0`、`sessionMode==='cloud'`、`allowOta===true` 且 `device_id + model + version` 齐备后触发检查。
  - 使用 `(device_id, model, version)` 组合作为页面生命周期内的去重键，避免重复请求。
- 红点联动流程
  - `detail.vue` 根据 `allowOta && otaCheckState.needUpgrade` 控制底部“参数设置”Tab 红点。
  - `params-tab.vue` 根据同一状态控制 OTA 行红点。
- 手动 OTA 流程
  - 若共享状态已确认有升级且已有 `firmwareUrl`，直接复用共享结果进入确认升级。
  - 若共享状态已确认无升级，直接提示“已是最新版本”。
  - 若共享状态未完成或缺少升级包信息，再调用 `appBatteryOtaCheck` 兜底并把结果回写给父级。
  - OTA 成功后通过事件把父级状态清空，移除红点，并允许未来基于新版本重新检测。

## 4. 安全与权限
- 仪表临时会话模式继续沿用 `allowOta=false`，不展示 OTA 入口，也不自动请求云端 OTA 检测。
- 自动检测失败仅记录控制台日志与错误状态，不向用户展示失败 toast，避免打扰正常使用。

## 5. 测试策略
- 以 `pnpm exec tsc --noEmit` 作为 UniApp 静态校验基线。
- 手工验证三类核心场景：
  - 自动检测命中新版本，红点双处联动。
  - 自动检测返回最新版本，无红点且手动点击仍提示最新。
  - 仪表临时会话隐藏 OTA，不触发自动检测。

## 6. 兼容性与迁移
- 不改动后端接口协议与返回结构。
- 不引入全局 store；OTA 提示状态仅在当前设备详情页生命周期内生效。
- 回滚时仅需恢复 `detail.vue` 与 `params-tab.vue` 的本次前端改动，不涉及数据库或接口迁移。
