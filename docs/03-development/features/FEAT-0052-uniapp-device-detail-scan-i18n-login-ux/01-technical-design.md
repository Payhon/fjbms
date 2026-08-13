# FEAT-0052 UniApp 设备详情、扫描、多语言与登录体验优化 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-08-13
- related_feature: FEAT-0052
- version: v0.1.0

## 1. 设计概述
- 仪表组件保留原组件结构和 canvas 绘制，顶部文本收敛为中间单个 SOC 百分比，左右轨道均使用 SOC。
- 高级参数弹层在“高级配置”区域新增只读 SOH 和虚拟容量写入入口，两者均受设备参数权限控制。
- 协议客户端 `writeRegisters` 增加可选 `targetAddress`，默认值保持原 BMS 客户端地址。
- 微信小程序自定义 TabBar 使用自绘 ActionSheet，避免原生取消按钮语言不可控。
- 登录守卫在共享 `ensureLoggedIn` 中做短时间全局节流和页面栈判断。
- 登录页与注册设置密码页通过平台编译条件设置协议初始值：`MP-WEIXIN` 为未勾选，非小程序保持已勾选。
- BLE discovery 使用应用级异步租约统一串行化，扫描页、首页自动连接和通用 BLE transport 不再各自独占页面级队列。

## 2. 关键实现
- SOC 仪表：
  - 非小程序 overlay 中间只显示一个 SOC 百分比与 SOC 文案。
  - 小程序 canvas 中间只绘制一个 SOC 百分比与 SOC 文案。
  - 左右轨道均使用 `props.soc / 100`。
  - 展示整数统一通过 `toSocDisplayInteger()` 先执行 `Math.trunc()`，再限制到 `0~100`；协议层的 `0.5%/Bit` 原始精度保持不变。
- 高级参数：
  - SOH 显示优先级：`status.energy.sohPct` -> `battery.soh` -> `-`。
  - 只读 SOH 权限 key 使用状态寄存器规范化值 `10d`，由后端设备参数权限树输出给后台权限管理配置。
  - 虚拟容量权限 key 使用寄存器规范化值 `627`，由后端设备参数权限树输出给后台权限管理配置。
  - “高级配置”分组仅在只读 SOH、虚拟容量写入或其他高级参数至少一个可见时展示。
  - 虚拟容量输入单位为 AH，写入前换算为 `Math.round(AH * 1000)`。
  - 写入寄存器：`0x0627` 起始两个寄存器，高字在前，targetAddress 为 `0x00`。
- 扫描信号：
  - `signalLevel` 按 `>= -80`、`>= -85`、`>= -90`、`>= -95`、否则 0 格映射。
- 扫描生命周期：
  - `common/ble/ble-discovery-coordinator.ts` 提供 FIFO 全局租约；租约覆盖 `startBluetoothDevicesDiscovery` 到对应 `stopBluetoothDevicesDiscovery` 的完整周期，释放操作幂等。
  - 扫描页在取得租约后才初始化/启动 discovery，启动成功后再设置 `isScanning=true`；退出时停止 discovery 后释放租约。
  - 扫描页 `onHide/onUnload` 复用同一个清理 Promise，不再由卸载回调直接关闭全局蓝牙适配器。
  - 扫描页 `onShow` 只刷新页面尺寸、已绑定设备列表和扫码模式分流，不调用 `startScan()`；普通进入、返回后再次进入及后台恢复均保持停止态，由用户点击按钮显式启动扫描。
  - 首页维护显式可见态；设备列表请求在首页隐藏后才返回时不得重新启动自动连接。`onHide` 同时调用 `invalidateBleConnectAttempts()`；正在执行的自动连接扫描最迟在下一次 250ms 活跃性检查中进入 `finally`、停止 discovery 并释放租约。
  - `connectBleClient()` 区分 `home_auto` 与交互式连接来源；用户点击开始扫描时仅取消仍在执行的首页临时 transport。`UniBleBmsTransport` 的 `createBLEConnection` 等待支持主动取消，使租约无需等到原生连接超时才释放；已成功缓存的连接与详情页交互连接不在取消集合内。
  - `ble-client-cache.ts` 与 `uni-ble-transport.ts` 的 discovery 同样取得全局租约，防止跨模块扫描重叠。
- 扫描错误策略：
  - `common/ble/ble-scan-error-policy.ts` 统一从 `errCode/code/errno` 或错误文本的 `code=` 中解析错误码。
  - `10001` 分类为蓝牙不可用，`10012` 分类为定位/权限问题，微信运行时出现的正数 `10008` 与兼容端出现的负数 `-30008` 均分类为扫描过于频繁；不再以错误文本是否包含 `Bluetooth` 判断蓝牙开关状态。
  - 首次 `10008/-30008` 时先停止残留 discovery，等待稳定窗口后重试一次；再次失败则展示准确提示且不打开系统蓝牙设置。
- 多语言：
  - 参数页新增固定文案 key。
  - 补齐高级参数常用参数名英文 key，降低回退到中文 label 的概率。
  - “我的”语言菜单固定展示 `语言/Language`。
- 登录跳转：
  - 当前页已是登录页时不导航。
  - 页面栈已有登录页且普通 navigateTo 时不重复压栈。
  - 1200ms 内重复触发只执行首次导航。
- 协议勾选：
  - `pages/login/login.vue` 与 `pages/login/register-password.vue` 使用 `getInitialAgreementChecked()` 初始化 `agree`。
  - 微信小程序编译目标返回 `false`，要求用户主动勾选《用户协议》和《隐私政策》后才能提交。
  - 非微信小程序编译目标返回 `true`，避免扩大 App/H5 行为变化。
- 首页蓝牙断开：
  - 用户主动断开时以释放本地 BLE 客户端和更新卡片通信态为准；底层断开命令失败时记录 warn，不再保留蓝牙态等待二次点击。
- 小程序 TabBar：
  - Home `onShow` 主动刷新自定义 TabBar 文案后再设置选中态，避免语言切换后跨 Tab 恢复中文。

## 3. 兼容性
- 普通读寄存器和默认写寄存器仍使用客户端默认 targetAddress。
- `writeParam` 调用不传 `targetAddress`，现有参数保存不受影响。
- 自定义 Add Device 弹层仅替换小程序自定义 TabBar 内的原生 ActionSheet，不影响 App 端 `useAddDeviceActionSheet`。
- 设备参数权限树新增只读 SOH 与虚拟容量节点，不新增后端接口或数据库字段。
- 协议勾选初始化只影响首次进入页面的默认值，不改变用户手动勾选、取消勾选和提交前校验逻辑。
- 全局租约只保护 discovery，不接管既有 BLE 连接请求队列和 OTA 独占队列；设备过滤与广播 MAC 解析保持不变。

## 4. 验证
- 静态校验：`cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
- SOC 展示规则断言：`cd fjbms-uniapp && pnpm dlx tsx common/soc-display.test.ts`
- BLE discovery 租约断言：`cd fjbms-uniapp && pnpm dlx tsx common/ble/ble-discovery-coordinator.test.ts`
- BLE 扫描错误分类断言：`cd fjbms-uniapp && pnpm dlx tsx common/ble/ble-scan-error-policy.test.ts`
- BLE 在途连接取消断言：`cd fjbms-uniapp && pnpm dlx tsx common/lib/bms-protocol/uni-ble-transport-connect-cancel.test.ts`
- 后端权限树单测：`cd backend && go test ./internal/service -run 'TestNormalizeDeviceParamPermissionKeys|TestBuildDeviceParamPermissionTreeUsesCanonicalKeys' -count=1`
- 人工抽测：设备详情、高级参数 SOH/虚拟容量权限显隐、高级参数写入、扫描中返回首页后立即再次进入 BLE 扫描、英文语言、小程序 Add Device、未登录首次打开、微信小程序登录/注册协议默认未勾选。
