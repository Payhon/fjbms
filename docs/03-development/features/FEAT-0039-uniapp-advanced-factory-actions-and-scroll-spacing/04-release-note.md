# FEAT-0039 UniApp 设备详情高级参数出厂命令补齐与底部遮挡修复 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-04-15
- related_feature: FEAT-0039
- version: v0.1.0

## 发布内容
- UniApp 设备详情“设置 > 高级参数 > 出厂配置”补齐以下工厂命令：
  - 擦除当前参数
  - 擦除历史记录
  - 擦除循环次数
  - 清除保护状态
  - 复位保护板
- 高级参数弹层新增底部滚动留白，修复末尾菜单被底部 Tab 挡住的问题。
- 后台设备参数权限树补齐上述新增工厂命令权限项。

## 影响范围
- `fjbms-uniapp/pages/device-battery/components/params-tab.vue`
- `fjbms-uniapp/lang/zh-CN.ts`
- `fjbms-uniapp/lang/en-US.ts`
- `backend/internal/service/device_param_permission_tree.go`

## 发布与回滚提示
- 发布前建议完成至少一轮移动端真机回归，重点检查底部滚动与点击可达性。
- 若需回滚，可移除新增工厂命令节点、弹层底部留白及对应权限树项。
