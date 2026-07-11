# FEAT-0068 移动端质保资料填写引导 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-07-10
- related_feature: FEAT-0068
- version: v0.1.0

## 1. 方案概览
- 后端在已有 `GET/POST /api/v1/app/warranty/profile` 响应中返回完成度与提醒状态，不增加新接口或 SQL。
- 设备绑定接口返回当前账号本次是否新增关联，移动端只在该标记为真时显示即时引导。
- UniApp 使用单一 Pinia store 管理提醒状态；App 生命周期、质保资料页和绑定流程复用该状态源。

## 2. 接口变更
- `GET/POST /api/v1/app/warranty/profile`
  - 新增 `warranty_profile_exists`，表示当前租户、当前用户在 `user_warranty_infos` 中是否存在记录。
  - 新增 `warranty_profile_completed`。
  - 新增 `warranty_profile_reminder_needed`，仅在当前终端用户有绑定设备且资料未完成时为真。
- `POST /api/v1/app/device/provision/bind`
  - 新增 `newly_bound`，仅本次新增 `device_user_bindings` 记录时为真。
- 均为响应新增字段，保持既有客户端兼容。

## 3. 关键规则
1. 资料完成度以同租户、同用户的 `user_warranty_infos` 记录存在且 `contact_name`、`contact_phone` 均为非空字符串判定。
2. profile 的 `contact_name`、`contact_phone` 只返回 `user_warranty_infos` 原始字段，禁止从 `users.name`、`users.username` 或 `users.phone_number` 回填；账号资料既不参与完成度计算，也不作为质保资料展示。
3. 绑定事务已存在当前用户关联时返回 `newly_bound=false`；新建关联后返回 `true`。
4. 绑定成功后，移动端先静默刷新 profile；仅 `newly_bound=true` 且 `warranty_profile_reminder_needed=true` 时展示对话框。
5. 前台检查不显示对话框，只刷新红点；请求失败时清除本地提示状态，不阻断既有功能。

## 4. 移动端交互
- App `onLaunch/onShow` 刷新提醒状态；首页 `onShow` 也刷新一次，覆盖冷启动后才完成登录的场景。
- 非微信小程序通过 `uni.showTabBarRedDot/hideTabBarRedDot` 操作“我的”Tab；微信小程序的自定义 TabBar 从共享存储与页面实例同步红点。
- 我的页质保入口展示红点；质保页展示文本提示条，不只依赖颜色传达提醒。`warranty_profile_exists=false` 时，个人质保信息卡显示明确空状态和“立即填写”按钮。
- “立即填写”以 `redirectTo` 进入 `pages/my/warranty/index?edit=1`，资料页加载后自动进入编辑态；“以后再说”保留原设备详情跳转。

## 5. 测试策略
- Go 单测覆盖 profile 完成度、账号回填排除、有无绑定设备、完整/不完整资料和绑定幂等/新增标记。
- UniApp 执行 TypeScript 检查与受影响文件静态校验。
- 真机/微信开发者工具验证 UUID 绑定、BLE 向导、原生 TabBar、微信自定义 TabBar、资料保存清理提示和网络异常降级。
