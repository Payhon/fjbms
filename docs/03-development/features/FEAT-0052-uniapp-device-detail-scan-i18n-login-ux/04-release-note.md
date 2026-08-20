# FEAT-0052 UniApp 设备详情、扫描、多语言与登录体验优化 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-08-13
- related_feature: FEAT-0052
- version: v0.1.0

## 1. 发布内容
- 设备详情仪表盘调整为中间只显示一个 SOC 百分比，左右进度条均跟随 SOC。
- 仪表盘 SOC 去除小数时改为直接截断，例如 `77.5%` 显示为 `77%`。
- 高级参数新增受设备参数权限控制的只读 SOH 与虚拟容量写入。
- BLE 扫描页信号格阈值优化。
- 补齐本次涉及的中英文文案，并修复小程序 Add Device 取消按钮语言。
- 优化未登录状态下的登录页跳转节流。
- 优化首页蓝牙设备主动断开体验，并修复小程序英文 TabBar 返回 Home 后文案回退中文的问题。
- 微信小程序登录页、注册设置密码页默认不再代用户勾选《用户协议》和《隐私政策》。
- 修复扫描中返回首页后再次进入蓝牙搜索可能无法发现设备并报 `10008/-30008 scanning too frequently` 的问题；首页自动连接、手动扫描和连接前清理现已全局串行。
- 修正扫描错误提示：扫描频率限制不再误提示系统蓝牙未开启，并会在停止残留扫描后自动退避重试一次。
- 蓝牙搜索页改为完全手动启动：进入页面默认保持“已停止扫描”，扫描中离开会自动停止，再次进入不会自动 Loading 或延迟后自行扫描。
- 用户点击“开始扫描”时会立即取消首页尚未完成的临时自动连接等待并释放 BLE 租约；已缓存的正常连接和详情页交互连接不受影响。
- 蓝牙仪表读取到后端 BMS 状态后，大扫码提示框会自动收起，顶部断开连接旁仍保留切换入口；点击入口可重新展开提示并扫码切换其他 BMS 板。

## 2. 影响范围
- `fjbms-uniapp` 移动端。
- 后台设备参数权限树。
- 协议文档 `doc/oriigin/device_comm_protocol_full.md`。

## 3. 发布前检查
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
- [x] `cd fjbms-uniapp && pnpm dlx tsx common/soc-display.test.ts`
- [x] `cd fjbms-uniapp && pnpm dlx tsx common/ble/ble-discovery-coordinator.test.ts`
- [x] `cd fjbms-uniapp && pnpm dlx tsx common/ble/ble-scan-error-policy.test.ts`
- [x] `cd fjbms-uniapp && pnpm dlx tsx common/lib/bms-protocol/uni-ble-transport-connect-cancel.test.ts`
- [x] `cd fjbms-uniapp && pnpm dlx tsx common/home-device-status.test.ts`
- [x] `cd fjbms-uniapp && pnpm dlx tsx pages/device-battery/meter-scan-handoff-policy.test.ts`
- [x] `cd fjbms-uniapp && git diff --check`
- [ ] `cd backend && go test ./internal/service -run 'TestNormalizeDeviceParamPermissionKeys|TestBuildDeviceParamPermissionTreeUsesCanonicalKeys' -count=1`
- [ ] 微信小程序英文环境 Add Device 弹层验证。
- [ ] 权限管理只读 SOH 节点与移动端显隐验证。
- [ ] 权限管理虚拟容量写入节点与移动端显隐验证。
- [ ] 设备详情高级参数写入虚拟容量验证。
- [ ] 微信小程序登录页、注册设置密码页协议默认未勾选验证。
- [ ] 微信小程序真机连续 20 次“扫描中返回首页并立即再次进入”，并分别覆盖首页蓝牙自动连接开启/关闭。
- [ ] Android、iOS App 扫描停止、立即二次扫描及选择设备连接回归。
- [ ] 微信小程序验证首次进入、扫描中返回后再次进入、后台恢复均保持停止态，且点击开始扫描无约 5 秒等待。
- [ ] 微信小程序、Android、iOS App 验证仪表读取 BMS 状态后大提示框自动收起、顶部入口显示，点击入口可重新展开并切换其他 BMS。

## 4. 回滚
- 回滚 FEAT-0052 对应移动端提交与协议文档更新。
- 若仅虚拟容量写入异常，可先隐藏写入入口并保留展示和语言优化。
- 若特定平台出现扫描协调兼容问题，可仅回滚 discovery 协调器、扫描错误分类及对应接入点，保留 FEAT-0052 其他功能。
