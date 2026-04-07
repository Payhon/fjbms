# FEAT-0035 后台通知设置短信配置回显修复 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-04-07 20:16
- related_feature: FEAT-0035
- version: v0.1.0

## 1. 实施记录
1. 排查 `frontend/src/views/management/notification/components/short-message.vue`，确认短信页的回填逻辑与邮箱页不一致。
2. 确认读取接口返回的业务数据包含 `config` JSON 字符串，但短信页未对默认配置与解析结果做稳定合并。
3. 新增 `createDefaultSMSConfig()`，统一短信配置默认值来源。
4. 新增 `resolveNotificationConfigPayload()` 与 `normalizeSMSConfig()`，兼容响应解包差异和 `config`/`sme_config` 两种来源。
5. 调整 `setTableData()`，改为字段级更新 `formModel` 和 `aliyun_sms_config`，避免整对象替换带来的回显不稳定。
6. 执行 `pnpm --dir frontend typecheck`，结果通过。

## 2. 待执行项
- 在运行环境回归验证短信配置页打开、保存、刷新后的完整回显链路。

## 3. 当前状态
- 代码修复与 TypeScript 静态校验已完成，当前处于 `review`，等待页面运行态验证。
