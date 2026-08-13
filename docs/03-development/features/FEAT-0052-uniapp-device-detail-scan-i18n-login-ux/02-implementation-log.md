# FEAT-0052 UniApp 设备详情、扫描、多语言与登录体验优化 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-08-13
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
17. 新增统一 SOC 展示转换函数，仪表盘不再使用 `Math.round()`，改为直接截断小数并限制在 `0~100`。
18. 根据微信小程序真机视频确认二次扫描失败的真实错误为 `startBluetoothDevicesDiscovery:fail system error, scanning too frequently (code=-30008)`，并确认系统蓝牙实际保持开启。
19. 新增应用级 BLE discovery FIFO 租约，统一串行化扫描页、首页自动连接、通用 BLE transport 的扫描及连接前停止扫描，避免旧页面/首页任务停止新页面扫描。
20. 首页增加显式可见态并在 `onHide` 使底层连接代次失效；首页隐藏后才完成的列表请求不再重新启动自动连接，正在执行的自动连接 discovery 在 250ms 分段检查后停止并释放租约。
21. 扫描页退出清理改为幂等 Promise，移除卸载时直接关闭全局适配器；原生扫描启动成功后才更新“正在扫描”状态。
22. 新增 BLE 扫描错误分类：`10001` 才提示打开系统蓝牙，`10012` 保持定位授权流程，`-30008` 停止残留扫描、退避 1000ms 并仅重试一次。
23. 向导页移除未协调的独立停止扫描调用，统一由 `UniBleBmsTransport.connect()` 在全局租约内完成“停止扫描、稳定等待、连接与服务发现”。
24. 根据 2026-08-13 测试反馈，取消扫描页 `onShow` 自动扫描：每次进入或返回页面均显示“已停止扫描”，只有用户点击“开始扫描”才调用 `startScan()`。
25. 用户主动点击开始扫描时使首页遗留的连接代次失效；自动连接 discovery 最迟在下一次 250ms 活跃性检查时停止并释放租约，避免手动扫描等待完整的 5 秒自动 discovery。
26. 保留 `onHide/onUnload -> stopScan()`，扫描中直接返回首页仍会自动停止 discovery、解绑发现回调并释放全局租约。
27. 根据 2026-08-13 真机截图补充微信运行时正数 `code=10008`，与已有 `-30008` 一并归类为扫描过于频繁，继续执行“停止残留扫描、退避、仅重试一次”的恢复流程。
28. 首页自动连接显式标记为 `home_auto`；手动扫描只取消仍在执行的首页临时 transport，并为 `createBLEConnection` 增加主动取消通道，使手动扫描无需等待原生连接超时即可取得全局 BLE 租约，不影响已缓存连接和详情页交互连接。

## 2. 已验证
- `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`：通过。
- `cd backend && go test ./internal/service -run 'TestNormalizeDeviceParamPermissionKeys|TestBuildDeviceParamPermissionTreeUsesCanonicalKeys' -count=1`：通过。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`：2026-05-16 通过。
- `cd backend && go test ./internal/service -run 'TestNormalizeDeviceParamPermissionKeys|TestBuildDeviceParamPermissionTreeUsesCanonicalKeys' -count=1`：2026-05-19 通过。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`：2026-05-19 通过。
- `cd fjbms-uniapp && pnpm dlx tsx common/soc-display.test.ts`：2026-08-12 通过。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`：2026-08-12 通过。
- `cd fjbms-uniapp && pnpm dlx tsx common/ble/ble-discovery-coordinator.test.ts`：2026-08-12 通过。
- `cd fjbms-uniapp && pnpm dlx tsx common/ble/ble-scan-error-policy.test.ts`：2026-08-12 通过。
- `cd fjbms-uniapp && pnpm dlx tsx common/home-device-status.test.ts`：2026-08-12 通过。
- 使用 `@vue/compiler-sfc` 解析并编译 `ble-scan.vue`、`provision-wizard.vue`、`home.vue` 的脚本块：2026-08-12 通过。
- `cd fjbms-uniapp && git diff --check`：2026-08-12 通过。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`：2026-08-13 通过。
- 使用 `@vue/compiler-sfc` 重新解析并编译 `ble-scan.vue`、`home.vue`：2026-08-13 通过。
- 静态检查确认 `ble-scan.vue` 的 `onShow` 不再调用 `startScan()`：2026-08-13 通过。
- `cd fjbms-uniapp && pnpm dlx tsx common/ble/ble-scan-error-policy.test.ts`：2026-08-13 通过，覆盖 `10008/-30008` 双形态频率限制错误。
- `cd fjbms-uniapp && pnpm dlx tsx common/lib/bms-protocol/uni-ble-transport-connect-cancel.test.ts`：2026-08-13 通过，在途原生连接取消未等待 6.5 秒超时且租约可再次取得。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`、SFC 脚本解析及 `git diff --check`：2026-08-13 通过。

## 3. 待验证
- 在微信小程序英文环境确认自定义弹层取消按钮显示为 `Cancel`。
- 在后台权限管理取消/勾选虚拟容量写入权限后，确认移动端高级参数入口随权限显隐。
- 在后台权限管理取消/勾选只读 SOH 权限后，确认移动端高级参数 SOH 随权限显隐。
- 使用可写设备确认虚拟容量写入帧与设备响应。
- 在微信开发者工具或真机小程序确认登录页、注册设置密码页首次进入时协议勾选为空，手动勾选后才能提交。
- 在微信小程序真机连续执行至少 20 次“扫描中返回首页并立即再次进入蓝牙搜索”，确认每次均能发现设备且不再出现 `10008/-30008`。
- 分别在首页蓝牙自动连接开启/关闭时验证二次扫描，并补充 Android、iOS App 真机回归；当前静态/逻辑测试不能替代真实 BLE 验收。
- 验证普通进入、扫描中返回后再次进入、应用后台恢复三种场景均保持停止态，且未点击“开始扫描”时按钮不出现 Loading、不会延迟后自行扫描。
