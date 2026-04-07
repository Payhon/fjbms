# FEAT-0036 后台短信验证码调试能力 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-04-07
- related_feature: FEAT-0036
- version: v0.1.0

## 1. 方案概览
- 在通知配置短信页新增一个管理员调试弹窗。
- `SYS_ADMIN` 场景下，弹窗增加租户下拉框，调试请求显式携带 `tenant_id`。
- 新增后端接口 `POST /api/v1/notification/services/config/sms/test`。
- 接口内部不走简单的“裸短信发送”，而是调用与移动端注册验证码一致的关键步骤：
  1. 解析手机号与场景。
  2. 读取租户 `auth_message_templates` 中 `SMS + scene` 的配置。
  3. 生成并缓存验证码。
  4. 读取 `notification_services_config` 的短信配置。
  5. 调用阿里云短信发送。

## 2. 接口与数据结构
### 2.1 请求
- 字段：
  - `tenant_id`
  - `phone_prefix`
  - `phone_number`
  - `scene`，限定为 `LOGIN / REGISTER / RESET_PASSWORD / BIND`

### 2.2 返回
- 返回统一调试结果对象：
  - `success`
  - `summary`
  - `phone`
  - `scene`
  - `provider`
  - `template_code`
  - `default_template_code`
  - `sign_name`
  - `endpoint`
  - `request_id`
  - `provider_code`
  - `provider_message`
  - `steps[]`
- `steps[]` 中逐项记录链路节点：
  - 租户识别
  - 手机号参数
  - 业务场景
  - APP认证短信模板
  - 验证码生成与缓存
  - 短信服务发送

## 3. 关键流程
### 3.1 诊断逻辑
- `AppAuth.DebugSendPhoneCode()` 负责完整调试编排。
- `NotificationServicesConfig.SendSMSByTemplateDetailed()` 负责在发送阶段返回更丰富的供应商诊断数据。
- 保留现有正式链路 `SendPhoneCode()` 和 `SendSMSByTemplate()` 行为不变，避免影响移动端现网逻辑。

### 3.2 错误信息展开
- 现有正式接口大多返回 `CodeParamError`，外层 message 为通用文案“请求参数验证失败”。
- 调试接口通过解析 `errcode.Error.Data`，把真实错误细节展开为结果区文本。

## 4. 安全与权限
- 调试接口限制为后台 `SYS_ADMIN` 账号调用。
- 返回结果中不包含 `access_key_secret` 等敏感配置。
- 仅展示调试所需的签名、模板 ID、Endpoint、RequestId 等定位信息。

## 5. 测试策略
- 前端：`pnpm --dir frontend typecheck`
- 后端：`go test ./...`
  - 若出现仓库现存失败用例，需确认非本次改动引入。
- 运行态：
  1. 打开后台短信配置页。
  2. 输入手机号并选择 `REGISTER`。
  3. 点击发送，核对结果区是否显示完整链路诊断。

## 6. 兼容性与迁移
- 不涉及数据库迁移。
- 不影响现有邮件调试接口。
- 不影响移动端正式发码接口入参与返回结构。
