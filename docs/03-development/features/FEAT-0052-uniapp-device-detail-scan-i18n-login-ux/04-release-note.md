# FEAT-0052 UniApp 设备详情、扫描、多语言与登录体验优化 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-05-19
- related_feature: FEAT-0052
- version: v0.1.0

## 1. 发布内容
- 设备详情仪表盘调整为中间只显示一个 SOC 百分比，左右进度条均跟随 SOC。
- 高级参数新增受设备参数权限控制的只读 SOH 与虚拟容量写入。
- BLE 扫描页信号格阈值优化。
- 补齐本次涉及的中英文文案，并修复小程序 Add Device 取消按钮语言。
- 优化未登录状态下的登录页跳转节流。
- 优化首页蓝牙设备主动断开体验，并修复小程序英文 TabBar 返回 Home 后文案回退中文的问题。
- 微信小程序登录页、注册设置密码页默认不再代用户勾选《用户协议》和《隐私政策》。

## 2. 影响范围
- `fjbms-uniapp` 移动端。
- 后台设备参数权限树。
- 协议文档 `doc/oriigin/device_comm_protocol_full.md`。

## 3. 发布前检查
- [ ] `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
- [ ] `cd backend && go test ./internal/service -run 'TestNormalizeDeviceParamPermissionKeys|TestBuildDeviceParamPermissionTreeUsesCanonicalKeys' -count=1`
- [ ] 微信小程序英文环境 Add Device 弹层验证。
- [ ] 权限管理只读 SOH 节点与移动端显隐验证。
- [ ] 权限管理虚拟容量写入节点与移动端显隐验证。
- [ ] 设备详情高级参数写入虚拟容量验证。
- [ ] 微信小程序登录页、注册设置密码页协议默认未勾选验证。

## 4. 回滚
- 回滚 FEAT-0052 对应移动端提交与协议文档更新。
- 若仅虚拟容量写入异常，可先隐藏写入入口并保留展示和语言优化。
