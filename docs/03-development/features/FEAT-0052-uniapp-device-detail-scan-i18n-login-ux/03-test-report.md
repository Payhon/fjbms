# FEAT-0052 UniApp 设备详情、扫描、多语言与登录体验优化 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-08-31
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
- 微信小程序登录页顶部返回入口及无页面历史时的首页访客态兜底。
- 扫描页、首页自动连接与通用 BLE transport 的全局 discovery 互斥和退出清理。
- `10008/-30008`、`10001`、`10012` 扫描错误分类及提示策略。
- 底部搜索入口的一次性自动启动、页面可见代次保护及 15/30 秒分模式超时。
- 二维码模式按合法目标 MAC 首次自动启动，及其与普通搜索、已绑定直达和异步页面退出的隔离。
- 自动停止后不手动清空而再次开始时，新一轮自动清理旧设备、排序状态和旧 MAC 对扫描降级的影响。
- 蓝牙仪表读取后端 BMS 状态后的扫码提示框自动收起、顶部切换入口保留与重新展开。

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
13. 仪表扫码 handoff 显隐策略断言
   - 命令：`cd fjbms-uniapp && pnpm dlx tsx pages/device-battery/meter-scan-handoff-policy.test.ts`
   - 覆盖：未读取 BMS 状态时显示大提示框、读取成功后自动收起并显示顶部入口、用户点击入口后可重新展开，以及云端会话、禁用 handoff、非蓝牙、连接中场景均隐藏。
   - 结果：2026-08-13 通过。
14. 本次仪表扫码入口静态校验
   - 命令：`cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
   - 方法：使用本地 `@vue/compiler-sfc` 解析并编译 `pages/device-battery/detail.vue` 脚本块；执行根仓与 UniApp `git diff --check`。
   - 结果：2026-08-13 通过。
15. BLE 搜索入口策略断言
   - 命令：`cd fjbms-uniapp && pnpm dlx tsx pages/device-provision/ble-scan-entry-policy.test.ts`
   - 覆盖：参数解析、仅首次普通入口消费、无标记/二维码不启用、登录拦截、扫描中状态、隐藏页面和旧可见代次阻断，以及普通 15 秒/二维码 30 秒超时。
   - 结果：2026-08-21 通过。
16. BLE 搜索入口路由断言
   - 命令：`cd fjbms-uniapp && node common/device-provision/ble-search-entry-route.test.js`
   - 覆盖：UniApp ActionSheet 与微信自定义 TabBar 搜索入口均携带 `auto_start=1`；普通搜索不使用 `entry_source=scan`，相机扫码匹配不携带普通自动搜索参数。
   - 结果：2026-08-21 通过。
17. 扫描稳定性逻辑回归
   - 命令：`cd fjbms-uniapp && pnpm dlx tsx common/ble/ble-scan-error-policy.test.ts && pnpm dlx tsx common/ble/ble-discovery-coordinator.test.ts && node common/device-provision/scan-routing.test.js`
   - 结果：2026-08-21 通过。
18. TypeScript 校验
   - 命令：`cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
   - 结果：2026-08-21 通过。
19. SFC 与差异检查
   - 方法：使用本地 `@vue/compiler-sfc` 解析并编译 `pages/device-provision/ble-scan.vue` 脚本块；执行根仓与 UniApp `git diff --check`。
   - 结果：2026-08-21 通过。
20. BLE 扫描列表稳定排序策略与调度断言
   - 命令：`cd fjbms-uniapp && pnpm dlx tsx pages/device-provision/ble-scan-list-order-policy.test.ts`
   - 覆盖：新设备末尾追加、二维码目标优先、RSSI 降序、无效 RSSI 置后、同值稳定顺序、连续广播 2 秒内单次重排、触摸暂停、600ms 恢复、停止最终刷新及清理迟到任务。
   - 结果：2026-08-21 通过。
21. 本次回归检查
   - 命令：自动搜索策略、入口路由、扫描错误分类、discovery 租约、BLE 连接取消、扫码路由和 `pnpm exec tsc --noEmit --pretty false`。
   - 方法：使用本地 `@vue/compiler-sfc` 编译 `pages/device-provision/ble-scan.vue` 脚本块。
   - 结果：2026-08-21 通过。
22. 微信小程序登录页返回入口静态校验
   - 命令：`cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`。
   - 方法：使用本地 `@vue/compiler-sfc` 解析并编译 `pages/login/login.vue` 的脚本与模板；检查入口受 `MP-WEIXIN` 条件编译约束，返回分支包含 `navigateBack -> switchTab -> reLaunch` 兜底链路。
   - 结果：2026-08-22 通过。
23. HBuilderX 微信小程序编译
   - 命令：`HBuilderX.app/Contents/MacOS/cli launch mp-weixin --project <fjbms-uniapp> --compile true --continue-on-error false`。
   - 结果：2026-08-22 编译成功；生成的登录页 WXML/WXSS/JS 包含返回入口及完整兜底链路。仅有既有 `ble-client-cache.ts` 鸿蒙 UA 检测警告，未上传、未提交审核。
24. 微信开发者工具运行态返回验证
   - 环境：微信开发者工具 Stable 2.02.2608040，本地 MP-WEIXIN 编译产物，`miniprogram-automator`。
   - 覆盖：登录页返回入口可见；通过 `navigateTo`、`redirectTo` 和直接 `reLaunch` 三类方式进入登录页后点击返回箭头，当前页面均为 `pages/home/home`。
   - 结果：2026-08-22 通过；截图保存为 `~/Desktop/fjbms-wechat-login-return-2026-08-22.png`。未上传代码、未提交审核。

25. 二维码首次自动搜索策略与页面生命周期模拟
   - 命令：`cd fjbms-uniapp && node pages/device-provision/ble-scan-auto-start.test.js`；`pnpm dlx tsx pages/device-provision/ble-scan-entry-policy.test.ts`。
   - 方法：内存转译并执行实际页面 `onLoad/onShow/onHide/onUnload` 和 `toggleScan` 处理，模拟绑定列表与原生扫描，不生成构建文件。
   - 覆盖：缺少 `auto_start` 的合法 QR 自动启动一次、非法/缺失 MAC 不启动、重复显示不重启、新导航实例再次启动、普通搜索显式 opt-in、已绑定直达、登录拦截、刷新延迟期间隐藏/卸载不启动或跳转、手动开始再停止不被覆盖、旧代次返回、刷新失败兜底和扫描失败不循环重试。
   - 结果：2026-08-31 通过；修改前新生命周期测试在“QR 首次开始次数”断言失败（实际 0、期望 1），修改后通过。此前第 15 项中的“二维码不启用”是历史策略，已被本次需求替代。
26. 扫码入口及既有行为回归
   - 命令：`node common/device-provision/ble-search-entry-route.test.js`、`node common/device-provision/scan-routing.test.js`；使用 `pnpm dlx tsx` 执行扫描列表排序、discovery 租约、扫描错误分类、详情来源、handoff、扫码 4G 宽限断言。
   - 结果：2026-08-31 全部通过；普通搜索仍为 `ble_search`，二维码仍为 `scan`，首页/组织列表保持无发现入口标记。
27. 类型与组件编译
   - 命令：`pnpm exec tsc --noEmit --pretty false`；使用 `@vue/compiler-sfc` 编译扫描页脚本与模板。
   - 结果：2026-08-31 通过。

28. 微信小程序编译与差异检查
   - 命令：`/Applications/HBuilderX.app/Contents/MacOS/cli launch mp-weixin --project /Users/payhon/work2025/project/fjbms/fjbms-uniapp --compile true --continue-on-error false`；根仓与 UniApp `git diff --check`。
   - 结果：2026-08-31 HBuilderX 5.24 编译成功（约 8 秒），差异检查通过；MP-WEIXIN 产物含 `targetMac` 入参、二维码自动启动分支与刷新后页面失效拦截。启动时提示 uniCloud 本地服务空间不存在，未阻断前端编译；没有运行真实 BLE、上传小程序或提交审核。

29. 重新开始扫描自动清理上轮列表
   - 命令：`cd fjbms-uniapp && node pages/device-provision/ble-scan-restart.test.js`。
   - 方法：内存执行实际 `startScan/stopScan/toggleScan`、超时、广播回调、`clearList` 和排序器，以假时钟驱动超时和 2 秒排序，以桩模拟 BLE API 和设备识别，不连接硬件。
   - 覆盖：自动超时保留列表、再次开始清空旧 Map/顺序、本轮 RSSI 正常排序且未再发现旧设备不残留、手动停止不清空、停止后忽略广播、新一轮无有效 MAC 恢复无 Service 过滤降级、同轮降级保留新结果、旧排序/触摸状态取消、本轮 600ms 触摸保护、启动失败空列表/提示/重试、隐藏页面不做列表清理。
   - 结果：2026-08-31 通过；修改前断言“再次开始应有 0 条旧记录”失败（实际 2），修改后通过。
30. 重新扫描增量静态回归
   - 命令：二维码生命周期模拟、搜索/扫码路由断言；使用 `pnpm dlx tsx` 执行排序、入口、discovery 租约、扫描错误分类与详情来源断言；`pnpm exec tsc --noEmit --pretty false`、扫描页 SFC 脚本与模板编译、根仓与 UniApp `git diff --check`。HBuilderX 微信小程序仅编译命令同第 28 项。
   - 结果：2026-08-31 全部通过，HBuilderX 5.24 编译约 8.5 秒，产物确认 session 有效性检查后先 `clearList()` 再申请租约与扫描。uniCloud 本地服务空间缺失提示未阻断编译；未上传或发布。原生扫描、设备广播和微信真机体验仍需独立验收。

## 3. 人工验证清单
- [ ] 自动扫描停止后，不点“清空列表”直接点“开始扫描”，旧结果立即清空，本轮重新发现的设备按当前信号排序；手动停止保留本轮结果。
- [ ] 上轮强信号设备移远或断电后不残留在新一轮；本轮无有效 MAC 时仍可降级重扫，降级过程不丢失本轮已展示设备。
- [ ] 关闭蓝牙后重新开始：旧列表清空、错误提示正常、可手动重试；Android/iOS App 和微信小程序分别验证。
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
- [ ] 从底部“＋ > 搜索”进入时无需点击即开始扫描，约 15 秒停止并保留已发现设备列表；按钮恢复为“开始扫描”。
- [ ] 普通直达蓝牙搜索页仍显示“已停止扫描”；底部“＋ > 扫码”识别合法 BMS MAC 后自动搜索一次，目标匹配窗口保持 30 秒，命中后自动停止扫描再进入向导。
- [ ] 扫码目标已绑定时直达详情、不多启动扫描；非法/缺失 MAC 不自动扫描；关闭蓝牙或拒绝授权时有错误提示和手动重试入口。
- [ ] 刷新绑定列表期间手动开始再停止、切后台、返回或卸载页面，迟到任务不得启动扫描或跳转；从向导返回不自动重启，新一次扫码创建页面后可再次自动启动。
- [ ] 自动扫描中不点击停止而直接返回首页，确认系统 discovery 自动停止；切后台或进入系统设置后返回仍保持停止态，不延迟自动重启。
- [ ] 再次进入后点击“开始扫描”，应快速进入扫描状态，不等待首页遗留的 5 秒自动 discovery。
- [ ] 首页蓝牙自动连接开启和关闭两种状态下，立即二次进入扫描都不存在空列表或错误弹窗。
- [ ] 模拟或捕获 `10008/-30008` 时只显示“扫描操作过于频繁”，不再弹“请先在系统设置中打开蓝牙”。
- [ ] 系统蓝牙确实关闭时仍能按 `10001` 弹出设置引导；定位服务/权限关闭时仍保持原授权流程。
- [ ] Android App、iOS App、微信小程序分别验证扫描、停止、再次扫描和选择设备进入向导连接。
- [ ] 首页自动连接开启/关闭两种状态下各连续 20 次执行“底部搜索—返回首页—立即再次进入”，每次均可发现设备且无 `10008/-30008`、空列表假扫描或连接失败。
- [ ] 多设备高频广播时，新设备立即出现在列表末尾，已有设备行最多约每 2 秒换位一次，实时信号图标仍正常变化。
- [ ] 手指按住或滚动列表时设备行不换位，松手后至少约 600ms 不重排；扫描过程中可直接准确点击目标设备并连接，无需先停止扫描。
- [ ] 英文下参数页无本次已知中文残留，Add Device 与语言切换菜单取消按钮显示 `Cancel`。
- [ ] 微信小程序英文环境从 My 切到 Home 后，底部 TabBar 仍显示英文。
- [ ] 未登录首次打开只跳转一次登录页。
- [ ] 首页蓝牙设备点击断开图标单次即可切换为断开状态。
- [ ] 微信小程序登录页、注册设置密码页首次进入时协议勾选为空，未勾选不可提交，手动勾选后可提交。
- [x] 微信开发者工具自动化从 `navigateTo` 进入登录页，顶部返回箭头返回首页。
- [x] 微信开发者工具自动化从 `redirectTo` 进入登录页，顶部返回箭头返回剩余页面栈中的首页。
- [x] 微信开发者工具自动化直接 `reLaunch` 登录页，顶部返回箭头通过无历史兜底切换到首页。
- [x] MP-WEIXIN 模拟器确认入口视觉并保存整改截图；条件编译产物确认非微信端模板不受影响。
- [ ] PACK 微信登录专属运行配置与微信真机确认返回入口，不触发登录、授权或重复提示。
- [ ] 使用整改截图重新提交微信审核；重新提审结果单独记录。
- [x] 显隐策略断言确认：仪表未读取 BMS 状态时显示大提示框；读取成功后收起提示框并显示顶部入口；用户重新展开后不会被同一已就绪状态再次关闭。
- [ ] 微信小程序、Android、iOS App 分别确认仪表读取后端 BMS 状态后顶部入口仍显示，点击入口可重新展开提示并扫码切换另一块 BMS。

## 4. 风险备注
- 2026-08-31 的页面生命周期测试只证明入口调度逻辑，未操作真实微信小程序或 BLE 硬件；本轮不以历史登录页的模拟器验证替代扫码/蓝牙验收。
- 当前仓库缺少 UniApp UI 自动化测试，UI 体验仍需真机或微信开发者工具抽测。
- 当前已确认返回分支源码、TypeScript、SFC、HBuilderX 编译和微信开发者工具运行态通过并保存模拟器截图；PACK 专属运行配置、微信真机和重新提审尚未完成。
- 定时器假时钟断言不能替代微信小程序、Android、iOS 对原生触摸事件顺序、滚动和 BLE 广播密度的真实验证。
- 本次已完成源码、逻辑断言与 SFC 语法校验；未在本机连接真实 BLE 设备，因此不能将上述结果视为 Android、iOS 或微信小程序真机闭环。
- 仪表扫码入口本次复用既有二维码校验和目标 MAC 配置流程；显隐测试通过不能替代扫码切换后端 BMS 的真实设备验证。
