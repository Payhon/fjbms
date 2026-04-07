# FEAT-0036 后台短信验证码调试能力 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-04-07 21:18
- related_feature: FEAT-0036
- version: v0.1.0

## 1. 实施记录
1. 排查移动端注册短信发码链路，确认后端 `app/auth/phone/code` 在多种业务错误下都会返回 `CodeParamError`，页面只能看到“请求参数验证失败”统一文案。
2. 确认后台通知配置页仅存在邮件调试能力，缺少短信验证码链路定位入口。
3. 新增后台调试接口 `notification/services/config/sms/test`。
4. 在 `AppAuth` 中增加调试编排方法，复用注册验证码链路的模板读取、验证码生成、短信发送逻辑。
5. 在短信发送服务中增加详细 provider 结果返回，补充模板 ID、签名、Endpoint、RequestId、供应商返回码与消息。
6. 在短信配置页增加调试弹窗、手机号/场景输入、结果面板展示。
7. 根据运行态排查结果，补充 `SYS_ADMIN` 租户下拉选择，并让调试接口显式接收 `tenant_id`，避免误用当前登录账号租户导致假阴性。
8. 根据真实短信发送结果继续排查，确认后端接口已返回 `data.success=true`，但前端短信调试页仍可能因响应对象层级差异将结果误判为失败提示。
9. 在短信调试页新增 `resolveSMSTestResult` 结果解包逻辑，统一兼容 `payload` / `payload.data` 两种返回形态，并补充异常兜底结果展示，保证成功短信不会再被前端误报失败。
10. 执行 `pnpm --dir frontend typecheck` 通过。
11. 执行定向验证，确认本次前端改动未引入新的类型错误；后端相关包此前已完成定向 `go test` 验证，全量测试仍受仓库既有 `project/initialize/test.TestSetDevice` 空指针失败影响。

## 2. 待执行项
- 在实际环境输入手机号测试 `REGISTER` 场景，确认短信是否收到，且前端 toast 与结果区都显示成功。

## 3. 当前状态
- 代码与静态验证已完成，当前等待运行态验收。
