# FEAT-0006 UniApp 升级检测与提示体验优化 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-04-10
- related_feature: FEAT-0006
- version: v0.1.0

## 1. 发布内容
- 设备详情页进入仪表盘后会自动执行一次 OTA 升级检测。
- 当设备存在可升级固件时，底部“参数设置”Tab 与参数页 OTA 行都会显示红点提示。
- OTA 行点击逻辑已兼容共享检测结果与兜底查询，避免用户必须先手动触发一次检测。

## 2. 影响范围
- `fjbms-uniapp/pages/device-battery/detail.vue`
- `fjbms-uniapp/pages/device-battery/components/params-tab.vue`

## 3. 升级步骤
- 前端重新构建并发布 `fjbms-uniapp`。
- 真机回归设备详情 OTA 检测、红点提示与 OTA 成功后的红点清除行为。

## 4. 回滚步骤
- 回滚本次 `detail.vue` 与 `params-tab.vue` 的 OTA 自动检测与红点改动。
- 恢复为“仅点击 OTA 行时触发检查”的旧行为。

## 5. 已知问题
- 若设备 OTA 成功后版本上报存在延迟，页面内即时复检可能无法立即反映新版本；重新进入设备详情页后会重新检测。
