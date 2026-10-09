# FEAT-0052 UniApp 设备详情、扫描、多语言与登录体验优化 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-09-28
- related_feature: FEAT-0052
- version: v0.1.0

## 1. 发布内容
- 2026-09-28 待发布增量：同一次 BMS 扫码完成连接后，详情断开并返回扫描页时不再因目标已绑定而自动进入详情重连；直接返回也保持停止态。重新扫描只更新列表，点击设备才连接，新一次扫码仍可自动匹配。
- 2026-08-31：扫描停止后再次点击“开始扫描”会自动清空上轮结果和排序状态，用户不必先手动清空。停止时仍保留结果，同轮内部降级重扫不会清空新结果；新一轮启动失败时旧结果不会恢复，沿用错误提示和手动重试。
- 设备详情仪表盘调整为中间只显示一个 SOC 百分比，左右进度条均跟随 SOC。
- 仪表盘 SOC 去除小数时改为直接截断，例如 `77.5%` 显示为 `77%`。
- 高级参数新增受设备参数权限控制的只读 SOH 与虚拟容量写入。
- BLE 扫描页信号格阈值优化。
- 补齐本次涉及的中英文文案，并修复小程序 Add Device 取消按钮语言。
- 优化未登录状态下的登录页跳转节流。
- 优化首页蓝牙设备主动断开体验，并修复小程序英文 TabBar 返回 Home 后文案回退中文的问题。
- 微信小程序登录页、注册设置密码页默认不再代用户勾选《用户协议》和《隐私政策》。
- 微信小程序登录页增加顶部返回箭头：有上一页时返回上一页，无上一页或返回失败时进入首页访客态，用户可拒绝登录后继续体验；App、H5 等端保持不变。
- 修复扫描中返回首页后再次进入蓝牙搜索可能无法发现设备并报 `10008/-30008 scanning too frequently` 的问题；首页自动连接、手动扫描和连接前清理现已全局串行。
- 修正扫描错误提示：扫描频率限制不再误提示系统蓝牙未开启，并会在停止残留扫描后自动退避重试一次。
- 底部“＋ > 搜索”进入蓝牙搜索页后会自动开始一次，普通搜索由 30 秒缩短为 15 秒；无标记普通直达保持手动。2026-08-31 起，扫码进入二维码匹配页且目标 MAC 合法时同样自动搜索一次，无需额外点击，匹配仍为 30 秒。
- 自动启动只在本次页面导航首次显示时消费；扫描中离开会自动停止，切后台或进入系统设置后返回不会自动重启，仍可点击按钮手动搜索。
- 蓝牙设备较多时，列表位置改为约每 2 秒统一排序；新设备立即追加到末尾，已有设备不再随每个 RSSI 广播包频繁跳动。
- 用户触摸或滚动列表时暂停重排，松手后保留 600ms 点击保护，使扫描过程中可以直接选择目标设备，无需先停止扫描。
- 用户点击“开始扫描”时会立即取消首页尚未完成的临时自动连接等待并释放 BLE 租约；已缓存的正常连接和详情页交互连接不受影响。
- 蓝牙仪表读取到后端 BMS 状态后，大扫码提示框会自动收起，顶部断开连接旁仍保留切换入口；点击入口可重新展开提示并扫码切换其他 BMS 板。

## 2. 影响范围
- 2026-09-28 增量仅修改共享扫描页的首次已绑定跳转条件与手动选择导航标记，适用于微信小程序及 Android/iOS App；沿用现有首次扫码、手动设备路由与详情断连，不新增接口、参数或全局状态。
- 2026-08-31 增量仅涉及共享扫描页入口策略、新一轮列表清理、异步刷新后的页面有效性检查及测试，微信小程序底部 TabBar 与 UniApp 扫码入口均适用；已绑定设备、仪表详情、UUID 绑定、首页暖连接和详情退出断连策略不变。不新增后端接口、权限或协议命令。
- `fjbms-uniapp` 移动端。
- 后台设备参数权限树。
- 协议文档 `doc/oriigin/device_comm_protocol_full.md`。

## 3. 发布前检查
- [x] 2026-09-28 返回重连回归先失败后通过，相关扫码/搜索路由和扫描/详情来源回归、TypeScript、扫描页 SFC 脚本/模板编译、HBuilderX 5.26 微信小程序编译及产物检查通过。
- [ ] 2026-09-28 微信小程序真机按视频验证断开后返回不重连、直接返回、后台恢复、手动重扫/设备点击及新一次扫码；Android/iOS App 冒烟。本机无可用调试手机，尚未提交、推送、上传或发布，状态保留 `in_progress`。
- [x] 2026-08-31 重新扫描列表清理隔离模拟、二维码生命周期和路由回归、BLE/详情来源策略、TypeScript、扫描页 SFC、HBuilderX 微信小程序编译及产物检查、根仓与 UniApp 差异检查。
- [ ] 微信小程序 Android/iOS 真机及 App 验证自动停止后直接重新开始、旧设备不残留、本轮信号排序、同轮降级结果保留及失败重试。
- [x] 2026-08-31 HBuilderX 5.24 微信小程序仅编译成功，产物包含二维码自动启动与页面失效拦截；根仓与 UniApp 差异检查通过。
- [x] 2026-08-31 二维码自动启动页面生命周期模拟、入口策略与路由、既有 BLE/详情来源回归、TypeScript 与扫描页 SFC 脚本/模板编译。
- [ ] 2026-08-31 增量：微信小程序 Android/iOS 真机底部“＋ > 扫码”自动搜索、30 秒超时、匹配跳转、蓝牙/授权失败、后台恢复及手动停止；Android/iOS App 共享逻辑回归。当前未发布或提交审核。
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
- [x] `cd fjbms-uniapp && pnpm dlx tsx common/soc-display.test.ts`
- [x] `cd fjbms-uniapp && pnpm dlx tsx common/ble/ble-discovery-coordinator.test.ts`
- [x] `cd fjbms-uniapp && pnpm dlx tsx common/ble/ble-scan-error-policy.test.ts`
- [x] `cd fjbms-uniapp && pnpm dlx tsx pages/device-provision/ble-scan-entry-policy.test.ts`
- [x] `cd fjbms-uniapp && pnpm dlx tsx pages/device-provision/ble-scan-list-order-policy.test.ts`
- [x] `cd fjbms-uniapp && node common/device-provision/ble-search-entry-route.test.js`
- [x] `pages/device-provision/ble-scan.vue` SFC 脚本编译
- [x] `pages/login/login.vue` SFC 脚本与模板编译
- [x] HBuilderX 5.24 微信小程序仅编译及 MP-WEIXIN 产物检查
- [x] 微信开发者工具自动化验证 `navigateTo`、`redirectTo`、直接 `reLaunch` 三类返回路径并保存整改截图
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
- [x] 微信小程序普通账号登录页验证顶部返回箭头，覆盖上一页返回、无历史首页兜底及 MP-WEIXIN 视觉截图。
- [ ] PACK 微信登录专页与微信真机验证顶部返回箭头及无登录/授权副作用。
- [ ] 使用整改截图重新提交微信审核。
- [ ] 微信小程序真机从底部“＋ > 搜索”确认自动开始、约 15 秒停止，并连续 20 次“扫描中返回首页并立即再次进入”，分别覆盖首页蓝牙自动连接开启/关闭。
- [ ] Android、iOS App 扫描停止、立即二次扫描及选择设备连接回归。
- [ ] 微信小程序验证普通直达保持手动、底部搜索只自动一次、扫描中返回及后台/系统设置恢复不自动重启，且按钮重试无约 5 秒等待。
- [ ] 微信小程序、Android、iOS 在多设备环境验证 2 秒稳定排序、触摸/滚动保护及扫描中直接选择设备连接。
- [ ] 微信小程序、Android、iOS App 验证仪表读取 BMS 状态后大提示框自动收起、顶部入口显示，点击入口可重新展开并切换其他 BMS。

## 4. 回滚
- 2026-09-28 增量可单独回滚已绑定跳转的 `shouldAutoStart && autoStartPending` 条件及手动选择时的标记消费，保留其余扫码、BLE 租约与详情断连逻辑；回滚将恢复返回时自动重连的已知问题。
- 若需恢复重新扫描时保留历史列表，仅移除 `startScan()` 中新增的 `clearList()` 调用；保留停止后的结果、手动清空按钮、扫码自动启动和全局 BLE 协调。
- 2026-08-31 扫码增量可仅回滚 `shouldScheduleBleScanAutoStart` 的二维码分支和页面目标 MAC 入参；保留普通搜索自动启动、全局 BLE 租约与 FEAT-0019 详情连接策略。
- 回滚 FEAT-0052 对应移动端提交与协议文档更新。
- 若仅虚拟容量写入异常，可先隐藏写入入口并保留展示和语言优化。
- 若特定平台出现扫描协调兼容问题，可仅回滚 discovery 协调器、扫描错误分类及对应接入点，保留 FEAT-0052 其他功能。
- 若特定平台的一次性自动启动出现兼容问题，可仅移除底部入口 `auto_start=1` 并恢复普通搜索 30 秒，不回滚全局 discovery 协调和错误分类保护。
- 若特定平台触摸事件兼容异常，可仅回滚稳定顺序调度和触摸监听，保留自动搜索、全局 discovery 协调及连接保护。
- 若微信小程序登录页返回入口出现布局或宿主导航兼容问题，可单独回滚该入口与返回处理，不影响现有登录和协议勾选流程。
