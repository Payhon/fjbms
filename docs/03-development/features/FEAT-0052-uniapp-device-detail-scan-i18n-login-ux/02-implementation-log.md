# FEAT-0052 UniApp 设备详情、扫描、多语言与登录体验优化 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-05-19
- related_feature: FEAT-0052
- version: v0.1.0

## 1. 实施记录
1. 更新 `dashboard-gauge`，将顶部数值收敛为中间单个 SOC 百分比，左右进度轨道均使用 SOC。
2. 更新 `params-tab`，高级配置区域新增只读 SOH 和虚拟容量写入入口。
3. 扩展 `BmsClient.writeRegisters`，支持单次写入传入 `targetAddress`。
4. 更新 BLE 扫描页 RSSI 信号格阈值。
5. 小程序自定义 TabBar 改为自绘 Add Device 弹层，补齐 Cancel 文案。
6. “我的”页面语言菜单固定显示 `语言/Language`。
7. 更新登录守卫，避免重复跳登录页。
8. 更新 `doc/oriigin/device_comm_protocol_full.md` 的虚拟容量命令说明。
9. 新增 FEAT-0052 文档并同步看板。
10. 在后端设备参数权限树中新增虚拟容量写入节点 `627`，移动端按同一权限 key 控制入口显隐。
11. 优化首页蓝牙断开：断开命令失败时也释放首页本地蓝牙态，避免二次点击。
12. Home 页小程序 `onShow` 主动刷新自定义 TabBar 文案，修复英文切换后返回 Home 恢复中文的问题。
13. “我的”页语言切换菜单改用可控 `u-action-sheet`，避免微信小程序原生取消按钮在英文环境仍显示中文。
14. 登录页与注册设置密码页新增平台化协议初始值，微信小程序默认不勾选《用户协议》和《隐私政策》，其它端保持原默认状态。
15. 后端设备参数权限树新增只读 SOH 节点 `10d`，移动端高级参数中的只读 SOH 改为按该权限显隐。
16. 高级配置分组改为按只读 SOH、虚拟容量写入和其他高级参数的可见性共同决定是否展示，避免空分组。

## 2. 已验证
- `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`：通过。
- `cd backend && go test ./internal/service -run 'TestNormalizeDeviceParamPermissionKeys|TestBuildDeviceParamPermissionTreeUsesCanonicalKeys' -count=1`：通过。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`：2026-05-16 通过。
- `cd backend && go test ./internal/service -run 'TestNormalizeDeviceParamPermissionKeys|TestBuildDeviceParamPermissionTreeUsesCanonicalKeys' -count=1`：2026-05-19 通过。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`：2026-05-19 通过。

## 3. 待验证
- 在微信小程序英文环境确认自定义弹层取消按钮显示为 `Cancel`。
- 在后台权限管理取消/勾选虚拟容量写入权限后，确认移动端高级参数入口随权限显隐。
- 在后台权限管理取消/勾选只读 SOH 权限后，确认移动端高级参数 SOH 随权限显隐。
- 使用可写设备确认虚拟容量写入帧与设备响应。
- 在微信开发者工具或真机小程序确认登录页、注册设置密码页首次进入时协议勾选为空，手动勾选后才能提交。
