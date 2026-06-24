# FEAT-0060 UniApp 详情状态与小程序品牌首屏优化 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-06-18
- related_feature: FEAT-0060
- version: v0.1.0

## 1. 方案概览
- 设备详情页增加 4G 设备判断和 `is_online` 展示分支，优先显示 `4G 在线` / `4G 离线`，BLE 状态保持原逻辑。
- 首页设备卡片增加 4G 设备判断，非蓝牙连接时按 `isOnline` 展示 `4G 在线` / `4G 离线`，不再对用户展示 MQTT 技术链路。
- 添加设备共享入口增加全局扫码流程锁，扫码期间和扫码成功跳转后的短时间内抑制 ActionSheet 重复弹出。
- 微信小程序端首页 Banner、登录 Logo 初始为空，运行配置返回后再按 PACK/非 PACK 和专属图片配置决定是否展示。

## 2. 接口与数据结构
- 不新增后端接口。
- 复用现有 `/api/v1/app/wxmp/runtime` 返回的 `source_type`、`login_only`、`home_banner_url`、`login_logo_url`。
- 复用设备详情/遥测中现有 `battery.is_online`、`bms_comm_type`、`comm_chip_id` 字段。

## 3. 关键流程
1. 详情页顶部状态：
   - `bms_comm_type` 为 2/3 或存在 `comm_chip_id` 时判定为 4G 设备。
   - 当前不是蓝牙连接且为 4G 设备时，按 `is_online === 1` 展示 `4G 在线`，否则展示 `4G 离线`。
   - `connType=bluetooth` 时仍展示蓝牙连接，避免双模设备蓝牙连接时被 4G 状态覆盖。
2. 首页卡片状态：
   - `bmsCommType` 为 2/3 时判定为 4G 设备。
   - 4G 设备非蓝牙连接时，在线显示 `4G 在线`，离线显示 `4G 离线`。
   - 蓝牙连接仍优先显示蓝牙连接，非 4G 设备保留原 MQTT/离线兜底。
3. 添加设备入口：
   - `showAddDeviceActionSheet` 读取全局 guard。
   - 扫码开始设置 `scanActive`，扫码完成/取消/无效码后释放，并设置短时间 `suppressUntil`。
   - 中间 Tab 页调用共享入口后，如返回 `false`，切回上一次 Tab，避免停留空白占位页。
4. PACK 首屏品牌：
   - 微信小程序端初始 Banner/Logo 为空，但首页 Banner 容器保留 421rpx 高度占位，避免首屏布局塌陷。
   - runtime 返回专属图片时展示专属图。
   - runtime 返回 PACK 且无专属图片时继续隐藏。
   - runtime 返回非 PACK 且无专属图片时回退默认富嘉图。

## 4. 安全与权限
- 不涉及权限模型和用户数据访问范围变化。
- 不暴露新的配置字段或密钥。

## 5. 测试策略
- 运行 UniApp TypeScript 校验和空白检查。
- Android APP 真机验证扫码相册跳转详情后的菜单关闭行为。
- 微信开发者工具或真机验证 PACK 小程序冷启动首屏无默认品牌闪现。

## 6. 兼容性与迁移
- APP/H5 非微信小程序端初始 Logo/Banner 继续显示默认图。
- 非 PACK 小程序配置返回后仍可回退默认图。
- 无数据库迁移。
