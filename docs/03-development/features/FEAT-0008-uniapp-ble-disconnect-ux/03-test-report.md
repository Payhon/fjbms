# FEAT-0008 UniApp 蓝牙信号展示与手动断开连接优化 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-09-28
- related_feature: FEAT-0008
- version: v0.1.0

## 1. 测试范围
- UniApp 蓝牙扫描页信号展示。
- 首页设备卡片断开蓝牙入口。
- 设备详情页断开蓝牙入口。
- “我的”自动连接开关默认关闭、用户选择持久化与首页自动连接开关判断。

## 2. 已执行
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`（自动连接兼容性修复后复测）
  - 结果：通过
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`（MAC 归一化修复后复测）
  - 结果：通过
- [x] `cd backend && go test ./internal/service -run TestDoesNotExist`
  - 结果：通过（仅编译校验，含 macOS 工具链告警，不影响结果）
- [ ] 真机/模拟器手动验证（扫描页、首页、详情页）
- [x] 2026-09-28 `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
  - 结果：通过。
- [x] 2026-09-28 Node 模拟实际 `onLoad`、开关 change、清除缓存与首页自动连接 handler
  - 缺失、`null`、空字符串、无效值均默认关闭；`0/false/off` 关闭，`1/true/on` 开启，含布尔值、数字及大小写/空格兼容，共 15 类存储值通过。
  - 初始渲染关闭；主动开启写入 `1` 并允许首页连接，关闭写入 `0` 并阻止首页连接；清除缓存及页面重进保留选择，均通过。
  - 原生存储与 BLE API 使用模拟实现，本项不代表真机 BLE 验收。
- [x] 2026-09-28 Vue SFC 编译
  - `pages/my/my.vue`、`pages/home/home.vue` 按 `MP-WEIXIN` / `APP-PLUS` 条件分支处理后，脚本与模板编译通过。
- [x] 2026-09-28 根仓库与 UniApp 子仓 `git diff --check`：通过。

## 3. 待执行
- [ ] 蓝牙连接设备：首页断开按钮点击后连接状态回落。
- [ ] 详情页蓝牙连接状态：断开按钮可见且可用。
- [ ] 非蓝牙状态：断开按钮隐藏。
- [ ] 扫描页信号强度显示为图标，无 dB 数字。
- [ ] Android/iOS/微信小程序真机未设置偏好时，确认“我的”开关关闭且首页不自动连接；主动开启、关闭及重启/清除缓存后按保存选择生效。

## 4. 缺陷与风险
- 目前未发现编译级缺陷。
- 仍需补充真机验证 BLE 断连体验（Android/iOS/微信小程序）。

## 5. 结论
- 代码改动已完成并通过 TypeScript 编译，当前处于真机验收阶段。
- 默认关闭增量已通过类型、页面编译与实际 handler 模拟检查，未打包发布。


## 2026-10-09 Git 交付前复核

- `pnpm exec tsc --noEmit --pretty false` 通过；首页和我的页在 `MP-WEIXIN` / `APP-PLUS` 分支的 SFC 脚本与模板编译通过。
- 复执行页面实际布尔偏好解析和切换 handler：15 类存储值、初始关闭、开启/关闭的 1/0 持久化及恢复默认值检查通过。
- 本轮按用户授权拆分 Git 提交并推送；未重新打包/发布移动端、部署服务或操作数据库，真机验收和功能状态保持原记录。
