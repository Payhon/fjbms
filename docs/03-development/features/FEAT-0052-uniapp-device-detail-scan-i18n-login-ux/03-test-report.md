# FEAT-0052 UniApp 设备详情、扫描、多语言与登录体验优化 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-05-19
- related_feature: FEAT-0052
- version: v0.1.0

## 1. 测试范围
- 设备详情仪表盘与高级参数。
- BLE 扫描页信号格。
- 中英文语言切换。
- 微信小程序自定义 Add Device 弹层。
- 未登录首次打开与添加设备入口。
- 后端设备参数权限树中的只读 SOH 与虚拟容量节点。
- 首页蓝牙连接设备主动断开。
- 微信小程序登录与注册设置密码页协议默认勾选状态。

## 2. 已执行
1. 静态校验
   - 命令：`cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
   - 结果：2026-05-16 通过；2026-05-19 通过。
2. 后端权限树单测
   - 命令：`cd backend && go test ./internal/service -run 'TestNormalizeDeviceParamPermissionKeys|TestBuildDeviceParamPermissionTreeUsesCanonicalKeys' -count=1`
   - 结果：通过；2026-05-19 通过。

## 3. 人工验证清单
- [ ] 仪表盘中间只显示一个 SOC 百分比和 SOC 文案，左右进度条均为 SOC 百分比。
- [ ] 高级参数展示只读 SOH。
- [ ] 后台权限管理可配置只读 SOH 权限，移动端高级参数 SOH 随权限显隐。
- [ ] 只取消 SOH、保留虚拟容量或其他高级参数时，高级配置分组仍显示；高级配置下无可见项时分组隐藏。
- [ ] 后台权限管理可配置虚拟容量写入权限，移动端入口随权限显隐。
- [ ] 虚拟容量输入 `50` 后发送目标地址 `0x00`、起始地址 `0x0627`、数据 `00 00 C3 50`。
- [ ] BLE 扫描页 RSSI `-80/-84/-89/-94/-96` 分别显示 `4/3/2/1/0` 格。
- [ ] 英文下参数页无本次已知中文残留，Add Device 与语言切换菜单取消按钮显示 `Cancel`。
- [ ] 微信小程序英文环境从 My 切到 Home 后，底部 TabBar 仍显示英文。
- [ ] 未登录首次打开只跳转一次登录页。
- [ ] 首页蓝牙设备点击断开图标单次即可切换为断开状态。
- [ ] 微信小程序登录页、注册设置密码页首次进入时协议勾选为空，未勾选不可提交，手动勾选后可提交。

## 4. 风险备注
- 当前仓库缺少 UniApp UI 自动化测试，UI 体验仍需真机或微信开发者工具抽测。
