# FEAT-0052 UniApp 设备详情、扫描、多语言与登录体验优化 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-05-19
- related_feature: FEAT-0052
- version: v0.1.0

## 1. 背景与目标
- 背景：
  - 移动端设备详情顶部仪表同时展示 SOC/SOH，不符合当前只突出 SOC 的展示要求。
  - 高级参数缺少只读 SOH 与虚拟容量写入能力。
  - BLE 扫描页信号格阈值偏保守，用户难以感知较好信号。
  - 英文语言下仍有参数项、微信小程序 Add Device 取消按钮等中文残留。
  - 未登录首次打开时多入口守卫可能连续跳转登录页。
  - 微信小程序登录/注册链路的用户协议与隐私政策勾选不得默认代用户同意。
- 目标：
  1. 设备详情顶部仪表只显示 SOC，左右进度条均使用 SOC。
  2. 高级参数展示只读 SOH，并支持虚拟容量按 AH 写入；只读 SOH 与虚拟容量入口均受设备参数权限控制。
  3. 按新阈值优化 BLE 信号格显示。
  4. 补齐本次涉及页面与小程序自定义 TabBar 的中英文文案。
  5. 登录守卫增加节流，避免重复跳登录页。
  6. 微信小程序环境下登录页与注册设置密码页的协议勾选默认未选中，必须由用户主动选择。

## 2. 范围
### In Scope
- `fjbms-uniapp/components/dashboard-gauge/`
- `fjbms-uniapp/pages/device-battery/components/params-tab.vue`
- `fjbms-uniapp/common/lib/bms-protocol/client.ts`
- `fjbms-uniapp/pages/device-provision/ble-scan.vue`
- `fjbms-uniapp/custom-tab-bar/`
- `fjbms-uniapp/lang/zh-CN.ts`、`fjbms-uniapp/lang/en-US.ts`
- `fjbms-uniapp/common/auth/ensure-login.ts`
- `fjbms-uniapp/pages/login/login.vue`
- `fjbms-uniapp/pages/login/register-password.vue`
- `backend/internal/service/device_param_permission_tree.go`
- `doc/oriigin/device_comm_protocol_full.md`

### Out of Scope
- 不新增后端接口。
- 不改变 SOC/SOH 协议解析、遥测上报与数据库结构。
- 不改动普通参数读取策略与现有 OTA 流程。

## 3. 验收标准
1. 仪表盘顶部只在中间展示一个 SOC 百分比与 SOC 文案，左右进度条均随 SOC 百分比变化。
2. 高级参数弹层可看到只读 SOH，值优先来自实时状态。
3. 只读 SOH 可在后台“系统管理 > 权限管理”的设备参数权限中通过 `10d` 节点配置，取消勾选后移动端高级参数不显示该值。
4. 虚拟容量入口可在后台“系统管理 > 权限管理”的设备参数权限中配置；输入 `50` 时按 `50000` 原始值写入 `0x0627~0x0628`，目标地址为 `0x00`。
5. BLE 扫描页 RSSI 信号格按 `-80/-85/-90/-95` 阈值显示。
6. 英文语言下参数页、Add Device 弹层取消按钮、“我的”语言菜单无本次已知中文残留。
7. 未登录首次打开或点击 Add Device 时只触发一次登录跳转；微信小程序切换英文后进入 Home，底部 TabBar 保持英文。
8. 首页蓝牙连接设备点击断开后单次操作即可更新为断开状态，不再要求二次点击。
9. 微信小程序登录页、注册设置密码页首次进入时协议勾选为空；未勾选时不能提交，用户手动勾选后可继续原登录/注册流程。

## 4. 风险与约束
- 虚拟容量命令目标地址与普通参数写入不同，必须使用专用 targetAddress，避免影响默认 `0x01` 参数写入。
- 微信小程序原生 `showActionSheet` 取消按钮受宿主语言影响，因此本次使用自定义弹层。
- 登录守卫节流只抑制短时间重复导航，不能屏蔽用户后续主动进入登录页。
- 协议默认勾选调整仅限微信小程序编译目标，其他端保持现有默认勾选行为以降低变更面。

## 5. 回滚方案
- 回滚 FEAT-0052 涉及的 UniApp 改动、协议文档更新与看板登记。
- 若虚拟容量现场验证异常，优先禁用高级参数中的入口，保留受权限控制的只读 SOH 与展示优化。
