# FEAT-0006 UniApp 升级检测与提示体验优化 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-10
- related_feature: FEAT-0006
- version: v0.1.0

## 1. 已执行验证
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`
- [ ] 真机 / HBuilderX 手工验收

## 2. 验证结果
- `cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过。

## 3. 待补充手工验收
- [ ] 云端设备进入设备详情页默认停留仪表盘时，自动触发一次 OTA 检测
- [ ] OTA 检测返回 `need_upgrade=false` 时，底部“参数设置”Tab 与参数页 OTA 行均无红点
- [ ] OTA 检测返回 `need_upgrade=true` 时，底部“参数设置”Tab 与参数页 OTA 行均显示红点
- [ ] 进入参数设置页后，OTA 行在红点旁显示灰色“新版本：{版本号}”
- [ ] 切换“仪表盘 / 电芯 / 参数设置 / 历史记录”后，OTA 红点状态保持一致
- [ ] 已自动检测出新版本时，点击 OTA 行直接进入升级确认，不重复执行无意义检测
- [ ] 自动检测尚未完成或缺少升级包信息时，点击 OTA 行仍能通过兜底检查继续升级
- [ ] OTA 成功后，两处红点同时消失
- [ ] 仪表临时会话模式仍隐藏 OTA 入口，且不出现任何 OTA 红点
- [ ] 自动检测失败时页面不弹错误 toast；随后手动点击 OTA 行仍可继续尝试
