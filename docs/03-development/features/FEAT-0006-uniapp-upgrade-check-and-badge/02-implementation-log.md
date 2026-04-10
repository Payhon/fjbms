# FEAT-0006 UniApp 升级检测与提示体验优化 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-10
- related_feature: FEAT-0006
- version: v0.1.0

## 日志
1. 2026-04-10 现状梳理
   - 确认 `params-tab.vue` 当前仅在点击 OTA 行时执行 `appBatteryOtaCheck`，设备详情页底部 Tab 没有可复用的 OTA 状态源。
   - 确认仪表临时会话通过 `allowOta=false` 隐藏 OTA 入口，需继续沿用该限制。
2. 2026-04-10 页面级状态上提
   - 在 `pages/device-battery/detail.vue` 新增 `DeviceOtaCheckState` 页面级状态，收敛自动检测结果与红点显隐逻辑。
   - 新增基于 `(device_id, model, version)` 的自动检测去重逻辑，仅在仪表盘默认页且必要字段齐备时触发一次。
3. 2026-04-10 红点与 OTA 行联动
   - 在设备详情页底部“参数设置”Tab 增加红点展示。
   - `params-tab.vue` 新增 `otaInfo / otaChecking / otaNeedUpgrade` props，并在 OTA 行标题旁增加红点提示。
4. 2026-04-10 手动 OTA 兜底与状态回写
   - `params-tab.vue` 优先复用父级共享 OTA 结果；仅在共享状态未完成或缺少升级包信息时再发起兜底检查。
   - OTA 成功后通过事件清空父级 OTA 红点状态，保持“只在升级成功或复检确认无升级时清除”的规则。
5. 2026-04-10 文档与看板
   - 新建 FEAT-0006 文档集。
   - 更新 `docs/04-project-tracking/board.md` 的 UniApp 泳道状态。
6. 2026-04-10 OTA 行提示补充
   - 参数页 OTA 固件升级项在命中新版本时，除红点外新增灰色“新版本：{版本号}”文案，便于用户直接识别目标版本。
