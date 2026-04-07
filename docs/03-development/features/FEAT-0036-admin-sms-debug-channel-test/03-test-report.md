# FEAT-0036 后台短信验证码调试能力 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-04-07
- related_feature: FEAT-0036
- version: v0.1.0

## 1. 测试范围
- 后台短信配置页调试弹窗展示。
- 调试接口请求与返回结构。
- 调试结果区格式化展示。
- 调试成功态 toast 与结果面板一致性。
- 前端 TypeScript 与后端编译测试。

## 2. 测试环境
- 工作区：`/Users/payhon/work2025/project/fjbms`
- 前端：`frontend/`
- 后端：`backend/`

## 3. 用例结果
- 已通过：`pnpm --dir frontend typecheck`
- 已通过：前端短信调试成功响应兼容 `payload.success` 与 `payload.data.success` 两种形态，避免接口已成功但页面仍提示失败。
- 已通过：此前定向后端验证 `go test ./internal/service ./internal/api ./internal/model ./router/apps`
- 已知存量失败：
  - `go test ./...`
  - 失败用例：`project/initialize/test.TestSetDevice`
  - 失败原因：`initialize/alarm_cache.go:105` 空指针
  - 结论：该失败与本次短信调试改动无关。
- 待执行：后台页面运行态回归与真实短信发送验证。
- 待执行：`SYS_ADMIN` 场景下租户切换后重新调试，确认不同租户模板读取正确。

## 4. 缺陷与风险
- 真实短信发送仍依赖阿里云供应商状态与模板审核状态。
- 若生产环境存在额外网关包装层，前端已做结果解包兼容，但仍建议保留运行态回归以覆盖真实部署链路。

## 5. 结论
- 本次改动具备提测条件，待运行态验证后可用于定位移动端短信验证码链路问题。
