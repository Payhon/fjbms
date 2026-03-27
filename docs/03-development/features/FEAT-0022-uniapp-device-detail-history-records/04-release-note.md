# FEAT-0022 UniApp 设备详情页历史记录功能 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-03-22
- related_feature: FEAT-0022
- version: v0.1.0

## 发布内容
- UniApp 设备详情页底部新增一级菜单“历史记录”。
- 历史记录页提供“保护次数记录 / 状态记录”二级切换。
- 新增 `0x4C / 0x4D` 协议读取能力，支持展示：
  - 历史保护次数摘要与分组列表
  - 最新优先的状态记录卡片
  - 连接异常、不支持、空记录、读取失败等移动端状态反馈

## 影响范围
- `fjbms-uniapp/common/lib/bms-protocol/`
- `fjbms-uniapp/pages/device-battery/detail.vue`
- `fjbms-uniapp/pages/device-battery/components/history-tab.vue`
- `fjbms-uniapp/lang/zh-CN.ts`
- `fjbms-uniapp/lang/en-US.ts`

## 发布与回滚提示
- 发布前建议完成 iOS / Android / 微信小程序三端真机回归。
- 若需回滚，可恢复设备详情页底部 3 Tab 结构，并移除 `0x4C / 0x4D` 协议扩展与历史记录组件。
