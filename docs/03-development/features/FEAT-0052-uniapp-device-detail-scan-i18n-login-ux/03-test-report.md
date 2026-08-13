# FEAT-0052 UniApp 设备详情、扫描、多语言与登录体验优化 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-08-13
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
- 扫描页、首页自动连接与通用 BLE transport 的全局 discovery 互斥和退出清理。
- `10008/-30008`、`10001`、`10012` 扫描错误分类及提示策略。

## 2. 已执行
1. 静态校验
   - 命令：`cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
   - 结果：2026-05-16 通过；2026-05-19 通过。
2. 后端权限树单测
   - 命令：`cd backend && go test ./internal/service -run 'TestNormalizeDeviceParamPermissionKeys|TestBuildDeviceParamPermissionTreeUsesCanonicalKeys' -count=1`
   - 结果：通过；2026-05-19 通过。
3. SOC 展示规则断言
   - 命令：`cd fjbms-uniapp && pnpm dlx tsx common/soc-display.test.ts`
   - 覆盖：半个百分点直接截断、普通小数不进位、整数不变、上下界限制和非法值回退。
   - 结果：2026-08-12 通过。
4. 本次变更 TypeScript 校验
   - 命令：`cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
   - 结果：2026-08-12 通过。
5. BLE discovery 租约断言
   - 命令：`cd fjbms-uniapp && pnpm dlx tsx common/ble/ble-discovery-coordinator.test.ts`
   - 覆盖：第二所有者等待、FIFO 交接、重复释放幂等、释放后无残留所有者。
   - 结果：2026-08-12 通过。
6. BLE 扫描错误分类断言
   - 命令：`cd fjbms-uniapp && pnpm dlx tsx common/ble/ble-scan-error-policy.test.ts`
   - 覆盖：从真机视频/截图同形错误文本解析 `-30008` 与 `10008`、`10001` 蓝牙不可用、`10012` 定位权限，以及 API 名包含 `Bluetooth` 时不得误判蓝牙关闭。
   - 结果：2026-08-12 通过。
7. 首页既有状态规则回归
   - 命令：`cd fjbms-uniapp && pnpm dlx tsx common/home-device-status.test.ts`
   - 结果：2026-08-12 通过。
8. Vue SFC 脚本解析
   - 方法：使用本地 `@vue/compiler-sfc` 解析并编译 `ble-scan.vue`、`provision-wizard.vue`、`home.vue` 的脚本块。
   - 结果：2026-08-12 通过。
9. 差异检查
   - 命令：`cd fjbms-uniapp && git diff --check`
   - 结果：2026-08-12 通过。
10. 手动启动扫描生命周期静态回归
   - 检查：`ble-scan.vue` 的 `onShow` 仅刷新页面/绑定设备状态，不调用 `startScan()`；`onHide/onUnload` 均调用幂等 `stopScan()`。
   - 检查：用户点击“开始扫描”进入 `startScan()` 后才取消在途自动连接并申请 discovery 租约。
   - 结果：2026-08-13 通过。
11. 本次反馈修复 TypeScript 与 SFC 校验
   - 命令：`cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
   - 方法：使用本地 `@vue/compiler-sfc` 解析并编译 `ble-scan.vue`、`home.vue` 脚本块。
   - 结果：2026-08-13 通过。
12. 首页在途连接取消断言
   - 命令：`cd fjbms-uniapp && pnpm dlx tsx common/lib/bms-protocol/uni-ble-transport-connect-cancel.test.ts`
   - 覆盖：原生 `createBLEConnection` 尚未回调时，手动取消无需等待 6.5 秒超时即可结束连接任务并归还全局 BLE 租约。
   - 结果：2026-08-13 通过。

## 3. 人工验证清单
- [ ] 仪表盘中间只显示一个 SOC 百分比和 SOC 文案，左右进度条均为 SOC 百分比。
- [x] SOC 展示转换断言确认 `77.5%` 输出 `77%`，不输出 `78%`。
- [ ] 在真机或微信开发者工具确认实时、云端 SOC 为 `77.5%` 时仪表盘显示 `77%`。
- [ ] 高级参数展示只读 SOH。
- [ ] 后台权限管理可配置只读 SOH 权限，移动端高级参数 SOH 随权限显隐。
- [ ] 只取消 SOH、保留虚拟容量或其他高级参数时，高级配置分组仍显示；高级配置下无可见项时分组隐藏。
- [ ] 后台权限管理可配置虚拟容量写入权限，移动端入口随权限显隐。
- [ ] 虚拟容量输入 `50` 后发送目标地址 `0x00`、起始地址 `0x0627`、数据 `00 00 C3 50`。
- [ ] BLE 扫描页 RSSI `-80/-84/-89/-94/-96` 分别显示 `4/3/2/1/0` 格。
- [ ] 微信小程序真机连续 20 次执行“扫描中返回首页并立即再次进入蓝牙搜索”，均能发现设备且不出现 `10008/-30008`。
- [ ] 普通进入蓝牙搜索页时显示“已停止扫描”，按钮为可点击的“开始扫描”，不自动扫描、不显示 Loading。
- [ ] 扫描中不点击停止而直接返回首页，确认系统 discovery 自动停止；再次进入仍保持停止态，不在约 5 秒后自动扫描。
- [ ] 再次进入后点击“开始扫描”，应快速进入扫描状态，不等待首页遗留的 5 秒自动 discovery。
- [ ] 首页蓝牙自动连接开启和关闭两种状态下，立即二次进入扫描都不存在空列表或错误弹窗。
- [ ] 模拟或捕获 `10008/-30008` 时只显示“扫描操作过于频繁”，不再弹“请先在系统设置中打开蓝牙”。
- [ ] 系统蓝牙确实关闭时仍能按 `10001` 弹出设置引导；定位服务/权限关闭时仍保持原授权流程。
- [ ] Android App、iOS App、微信小程序分别验证扫描、停止、再次扫描和选择设备进入向导连接。
- [ ] 英文下参数页无本次已知中文残留，Add Device 与语言切换菜单取消按钮显示 `Cancel`。
- [ ] 微信小程序英文环境从 My 切到 Home 后，底部 TabBar 仍显示英文。
- [ ] 未登录首次打开只跳转一次登录页。
- [ ] 首页蓝牙设备点击断开图标单次即可切换为断开状态。
- [ ] 微信小程序登录页、注册设置密码页首次进入时协议勾选为空，未勾选不可提交，手动勾选后可提交。

## 4. 风险备注
- 当前仓库缺少 UniApp UI 自动化测试，UI 体验仍需真机或微信开发者工具抽测。
- 本次已完成源码、逻辑断言与 SFC 语法校验；未在本机连接真实 BLE 设备，因此不能将上述结果视为 Android、iOS 或微信小程序真机闭环。
