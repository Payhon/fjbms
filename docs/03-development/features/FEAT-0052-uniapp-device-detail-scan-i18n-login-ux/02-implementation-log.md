# FEAT-0052 UniApp 设备详情、扫描、多语言与登录体验优化 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-09-28
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
29. 将仪表扫码 handoff 能力与提示框展开状态解耦：新增显隐策略和断言测试，首次读取到后端 BMS 状态时自动收起大提示框并显示顶部入口；点击入口可重新展开提示框并继续扫码，后续状态轮询不会再次强制收起。
30. 根据 2026-08-21 客户操作习惯，仅为 UniApp ActionSheet 与微信自定义 TabBar 的“搜索”入口增加 `auto_start=1`；相机扫码匹配及其他直达入口保持原行为，普通搜索不复用 `entry_source=scan`。
31. 扫描页新增导航实例级自动启动消费标记、待执行标记和页面可见代次：首次 `onShow` 刷新绑定列表后自动启动一次，切后台、进入设置、重复 `onShow`、旧异步刷新及用户主动操作均不会触发迟到或重复启动。
32. 普通搜索超时由 30 秒缩短为 15 秒，二维码目标匹配继续保持 30 秒；扫描过滤降级、频率限制退避、全局租约、退出清理以及选择设备前先停止扫描的流程不变。
33. 新增入口策略和路由断言，覆盖参数解析、一次性消费、页面代次保护、15/30 秒分模式时长以及两套底部入口参数。
34. 将扫描列表从“响应式 Map 每次更新后立即排序”改为“实时设备 Map + 稳定设备 ID 顺序”；新设备立即追加末尾，已有设备的名称、RSSI、MAC 和信号图标实时更新但不立即换位。
35. 新增 2,000ms 排序调度器和 600ms 触摸释放保护；连续广播复用单个排序任务，触摸/滚动时暂停，停止扫描时刷新最终顺序，清空、隐藏、卸载和 session 失效时取消迟到任务。
36. 排序继续保持二维码目标优先和 RSSI 降序，并为相同/无效 RSSI 保留上轮相对顺序；设备行保留稳定 `deviceId` key，不增加移动动画。
37. 新增纯排序及假时钟测试，覆盖追加、目标优先、稳定同值排序、2 秒节流、触摸暂停/600ms 恢复、最终刷新和任务取消。
38. 根据微信登录环节审核意见，仅在 `MP-WEIXIN` 登录页增加圆形顶部返回箭头；有页面历史时返回上一页，页面栈仅有登录页或原生返回失败时切换到首页，切换 Tab 失败再使用 `reLaunch` 兜底，使用户可以拒绝登录并继续访客体验。

39. 2026-08-31 根据扫码进入后未自动搜索的反馈，在共享入口策略中允许 `mode=qr` 且规范化 MAC 合法时自动启动一次，无需各扫码入口补 `auto_start=1`；无标记普通入口、已绑定设备、仪表详情、UUID 绑定和详情来源策略保持不变。
40. 刷新绑定列表后先检查页面可见性、登录守卫和可见代次，防止已失效任务启动扫描或跳转详情；保留首次消费、按钮操作取消、隐藏/卸载停止和 15/30 秒超时规则。
41. 新增实际页面生命周期与按钮处理的隔离模拟测试：修改前复现二维码首次启动次数为 0，修改后覆盖首次启动、新导航实例、重复显示、后台返回、手动开始/停止、已绑定直达、非法 MAC、登录拦截、刷新失败与启动失败不循环重试。

42. 2026-08-31 按用户选择采用“重新开始自动清理上轮列表”方案：在 `startScan()` 的页面/session 校验之后复用 `clearList()`，只清理扫描结果、显示顺序和排序调度状态。超时/手动停止保留结果，同一轮无 Service 过滤降级不清空，绑定缓存、详情连接和扫码来源策略不变。
43. 新增 `ble-scan-restart.test.js`，使用实际扫描入口、停止、超时、广播处理与排序器配合假时钟/原生 BLE 桩验证跨轮行为；修改前在再次开始后仍有 2 条旧数据处失败，修改后通过。
44. 2026-09-28 根据微信录屏定位扫码返回重连：首次扫描和自动匹配已被消费，但绑定成功后返回触发 `onShow`，原已绑定目标分支仍无条件跳转详情，详情初始化随即重连。为该分支增加 `shouldAutoStart && autoStartPending` 条件，不新增跨页状态。
45. 手动选择设备时消费已有 `navigated` 标记并取消待执行自动任务，返回后重新扫描只更新列表，用户仍可点击设备连接；首次匹配、首次已绑定直达和新一次扫码继续可用。
46. 扩展既有生命周期测试，执行实际自动匹配、设备选择和页面显示处理器，模拟绑定列表从未绑定变为已绑定；修改前在“返回不得重定向”断言失败（实际 1、期望 0），修复后全部通过。

## 2. 已验证
- 2026-09-28 返回体验增量：二维码生命周期、扫描列表重启、扫码/搜索入口路由、扫描入口与详情来源共 6 组回归通过；`pnpm exec tsc --noEmit --pretty false` 与扫描页 SFC 脚本/模板编译通过。
- 2026-09-28：HBuilderX 5.26 微信小程序仅编译成功，开发产物确认已绑定目标首次入口条件和手动选择的导航标记；uniCloud 本地服务空间缺失提示未阻断前端编译。未提交、推送、上传或发布。
- 2026-08-31 重新扫描增量：`node pages/device-provision/ble-scan-restart.test.js`、二维码生命周期与两组入口路由回归、排序/入口/租约/错误分类/详情来源共 5 组策略断言、`pnpm exec tsc --noEmit --pretty false` 和扫描页 SFC 脚本/模板编译通过。HBuilderX 5.24 微信小程序仅编译成功，产物确认新一轮入口包含 `clearList()`；根仓与 UniApp `git diff --check` 通过。uniCloud 本地服务空间缺失提示未阻断前端编译，未上传或发布。
- 2026-08-31：HBuilderX 5.24 微信小程序仅编译成功，产物确认含二维码目标 MAC 自动启动分支和页面可见代次检查；根仓与 UniApp `git diff --check` 通过。编译前提示 uniCloud 本地服务空间不存在，但未阻断编译；本次未上传或发布。
- 2026-08-31：`node pages/device-provision/ble-scan-auto-start.test.js`、`node common/device-provision/ble-search-entry-route.test.js`、`node common/device-provision/scan-routing.test.js` 均通过。
- 2026-08-31：使用 `pnpm dlx tsx` 执行扫描入口策略、扫描列表排序、discovery 租约、扫描错误分类、详情来源、handoff、扫码 4G 宽限共 7 组断言，均通过；`pnpm exec tsc --noEmit --pretty false` 与扫描页 SFC 脚本/模板编译通过。
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
- `cd fjbms-uniapp && pnpm dlx tsx pages/device-battery/meter-scan-handoff-policy.test.ts`：2026-08-13 通过，覆盖未读取状态的大提示、读取成功后的顶部入口、主动重新展开及禁用场景。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`、`detail.vue` SFC 脚本编译、根仓与 UniApp `git diff --check`：2026-08-13 通过。
- `cd fjbms-uniapp && pnpm dlx tsx pages/device-provision/ble-scan-entry-policy.test.ts`：2026-08-21 通过，覆盖一次性自动启动、重复/后台/迟到任务阻断和 15/30 秒超时策略。
- `cd fjbms-uniapp && node common/device-provision/ble-search-entry-route.test.js`：2026-08-21 通过，确认两套底部搜索入口携带 `auto_start=1` 且普通搜索不使用扫码来源标记。
- `cd fjbms-uniapp && pnpm dlx tsx common/ble/ble-scan-error-policy.test.ts`、`pnpm dlx tsx common/ble/ble-discovery-coordinator.test.ts`、`node common/device-provision/scan-routing.test.js`：2026-08-21 通过。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`：2026-08-21 通过。
- 使用本地 `@vue/compiler-sfc` 解析并编译 `pages/device-provision/ble-scan.vue` 脚本块，执行根仓与 UniApp `git diff --check`：2026-08-21 通过。
- `cd fjbms-uniapp && pnpm dlx tsx pages/device-provision/ble-scan-list-order-policy.test.ts`：2026-08-21 通过，覆盖稳定顺序、2 秒调度、600ms 触摸保护、停止最终刷新和迟到任务取消。
- 自动搜索策略/路由、扫描错误分类、discovery 租约、连接取消、扫码路由、UniApp TypeScript 与 `ble-scan.vue` SFC 脚本回归：2026-08-21 通过。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`：2026-08-22 通过。
- 使用本地 `@vue/compiler-sfc` 解析并编译 `pages/login/login.vue` 的脚本与模板：2026-08-22 通过。
- 使用 HBuilderX 5.24 CLI 执行微信小程序仅编译：2026-08-22 通过；产物确认包含返回按钮结构、样式及 `navigateBack -> switchTab -> reLaunch` 处理。编译仅出现既有鸿蒙 UA 检测警告，未上传代码。
- 使用微信开发者工具 Stable 2.02.2608040 与 `miniprogram-automator` 运行本地编译产物：2026-08-22 通过；`navigateTo`、`redirectTo` 和直接 `reLaunch` 三类登录页入口点击返回箭头后均进入首页。整改截图保存为 `~/Desktop/fjbms-wechat-login-return-2026-08-22.png`，未执行预览上传或审核提交。

## 3. 待验证
- 2026-09-28 增量：微信小程序 Android/iOS 真机按反馈录屏执行“未绑定 BMS 扫码 -> 绑定成功 -> 详情主动断开 -> 返回扫描页”，确认保持停止态、不再次进入详情或连接；直接返回、重复显示、后台恢复、手动重扫与点击设备、新一次扫码同步验证，并在 Android/iOS App 冒烟。本机 `adb devices -l` 无设备，`xcrun devicectl list devices` 列出的手机均不可用，未执行真机蓝牙验收。
- 微信小程序 Android/iOS 真机“自动停止 -> 不清空直接开始”反复验证：旧列表自动消失、本轮设备按新 RSSI 排序；设备移远/断电后不残留在新一轮，手动停止保留列表，启动失败展示错误且可重试。Android/iOS App 同步回归共享页面行为。
- 微信小程序 Android/iOS 真机从底部“＋ > 扫码”识别未绑定 BMS MAC，确认无需点击即可扫描、命中目标后停止扫描再进入向导；蓝牙关闭/拒绝授权时沿用提示和手动重试，返回/后台不重复启动，新一次扫码可重新自动启动。
- Android/iOS App 回归共享扫码策略；保留首页 30 秒暖连接与发现入口退出断连行为。本轮生命周期模拟使用假的 BLE 与绑定列表，不能替代真实原生蓝牙验证。
- 在微信小程序英文环境确认自定义弹层取消按钮显示为 `Cancel`。
- 在后台权限管理取消/勾选虚拟容量写入权限后，确认移动端高级参数入口随权限显隐。
- 在后台权限管理取消/勾选只读 SOH 权限后，确认移动端高级参数 SOH 随权限显隐。
- 使用可写设备确认虚拟容量写入帧与设备响应。
- 在微信开发者工具或真机小程序确认登录页、注册设置密码页首次进入时协议勾选为空，手动勾选后才能提交。
- 在 PACK 微信登录专属运行配置和微信真机中确认顶部箭头显示与首页兜底，返回时不触发登录、授权或重复提示；使用已保存的整改截图重新提审并记录审核结果。
- 在微信小程序真机连续执行至少 20 次“扫描中返回首页并立即再次进入蓝牙搜索”，确认每次均能发现设备且不再出现 `10008/-30008`。
- 分别在首页蓝牙自动连接开启/关闭时验证二次扫描，并补充 Android、iOS App 真机回归；当前静态/逻辑测试不能替代真实 BLE 验收。
- 验证底部“＋ > 搜索”首次进入自动开始并约 15 秒停止；扫描中返回、应用后台恢复及系统设置返回均保持停止态，且不会延迟后自行扫描。
- 验证普通直达搜索页仍为手动启动、二维码目标匹配仍使用 30 秒，并确认发现设备后停止 discovery 再进入连接流程。
- 在设备较多的环境验证新设备立即追加、已有设备约每 2 秒才重排，触摸/滚动及点击过程中不换位，并确认扫描中可直接选中目标设备完成连接。
- 在微信小程序、Android、iOS App 分别验证仪表读取后端 BMS 状态后大提示框自动收起、顶部入口显示；点击入口重新展开并扫码切换另一块 BMS 后，应重新读取新板状态。
