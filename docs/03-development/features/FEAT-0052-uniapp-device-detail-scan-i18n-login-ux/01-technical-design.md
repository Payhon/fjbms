# FEAT-0052 UniApp 设备详情、扫描、多语言与登录体验优化 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-05-19
- related_feature: FEAT-0052
- version: v0.1.0

## 1. 设计概述
- 仪表组件保留原组件结构和 canvas 绘制，顶部文本收敛为中间单个 SOC 百分比，左右轨道均使用 SOC。
- 高级参数弹层在“高级配置”区域新增只读 SOH 和虚拟容量写入入口，两者均受设备参数权限控制。
- 协议客户端 `writeRegisters` 增加可选 `targetAddress`，默认值保持原 BMS 客户端地址。
- 微信小程序自定义 TabBar 使用自绘 ActionSheet，避免原生取消按钮语言不可控。
- 登录守卫在共享 `ensureLoggedIn` 中做短时间全局节流和页面栈判断。
- 登录页与注册设置密码页通过平台编译条件设置协议初始值：`MP-WEIXIN` 为未勾选，非小程序保持已勾选。

## 2. 关键实现
- SOC 仪表：
  - 非小程序 overlay 中间只显示一个 SOC 百分比与 SOC 文案。
  - 小程序 canvas 中间只绘制一个 SOC 百分比与 SOC 文案。
  - 左右轨道均使用 `props.soc / 100`。
- 高级参数：
  - SOH 显示优先级：`status.energy.sohPct` -> `battery.soh` -> `-`。
  - 只读 SOH 权限 key 使用状态寄存器规范化值 `10d`，由后端设备参数权限树输出给后台权限管理配置。
  - 虚拟容量权限 key 使用寄存器规范化值 `627`，由后端设备参数权限树输出给后台权限管理配置。
  - “高级配置”分组仅在只读 SOH、虚拟容量写入或其他高级参数至少一个可见时展示。
  - 虚拟容量输入单位为 AH，写入前换算为 `Math.round(AH * 1000)`。
  - 写入寄存器：`0x0627` 起始两个寄存器，高字在前，targetAddress 为 `0x00`。
- 扫描信号：
  - `signalLevel` 按 `>= -80`、`>= -85`、`>= -90`、`>= -95`、否则 0 格映射。
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

## 4. 验证
- 静态校验：`cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
- 后端权限树单测：`cd backend && go test ./internal/service -run 'TestNormalizeDeviceParamPermissionKeys|TestBuildDeviceParamPermissionTreeUsesCanonicalKeys' -count=1`
- 人工抽测：设备详情、高级参数 SOH/虚拟容量权限显隐、高级参数写入、BLE 扫描、英文语言、小程序 Add Device、未登录首次打开、微信小程序登录/注册协议默认未勾选。
