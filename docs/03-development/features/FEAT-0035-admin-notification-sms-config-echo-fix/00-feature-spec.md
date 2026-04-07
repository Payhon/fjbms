# FEAT-0035 后台通知设置短信配置回显修复 - 功能规格

- status: review
- owner: payhon
- last_updated: 2026-04-07
- related_feature: FEAT-0035
- version: v0.1.0

## 1. 背景与目标
- 背景：
  - 后台管理 `系统管理 > 通知设置 > 短信` 页面请求 `GET /notification/services/config/SME_CODE` 后，接口返回的 `config` 字段已包含阿里云短信配置，但表单中的 `AccessKeyID`、`AccessKeySecret`、`签名`、`默认模板ID` 未正常回显。
  - 当前页面仅保留默认值，导致管理员误以为配置为空，存在误改或重复录入风险。
- 目标：
  1. 修复短信配置页对 `config` 的解析与表单回填。
  2. 保证接口已保存的阿里云短信配置可稳定显示在页面表单中。
  3. 不改变现有通知配置接口结构与保存 payload 结构。

## 2. 范围
### In Scope
- `frontend/src/views/management/notification/components/short-message.vue`
- 短信配置响应解包与 `config` 解析。
- 短信表单默认值与嵌套对象回填逻辑。
- 文档与看板同步回写。

### Out of Scope
- 不修改后端 `notification/services/config` 接口返回格式。
- 不新增短信服务商类型。
- 不调整短信配置保存接口字段定义。

## 3. 用户价值
- 系统管理员打开短信配置页时可以直接看到已保存的阿里云短信参数。
- 避免因表单错误显示为空而重复录入或误覆盖线上配置。

## 4. 验收标准
1. 打开 `系统管理 > 通知设置 > 短信`，接口返回的 `config` 中若存在 `provider`、`access_key_id`、`access_key_secret`、`endpoint`、`sign_name`、`template_code`，页面需正确回显。
2. 当接口仅返回部分字段时，未返回字段使用前端默认值补齐，不出现运行时报错。
3. 保存后重新拉取配置，页面仍能正确回显已保存值。
4. 本次改动不引入 TypeScript 编译错误。

## 5. 风险与约束
- 短信配置表单为多层嵌套对象，若直接整对象替换响应式子对象，存在表单回显或后续编辑异常风险。
- 需要兼容接口层可能返回“已解包对象”或“包含 `data` 包裹对象”的场景，避免前端因响应形态差异丢失数据。

## 6. 回滚方案
- 回滚 `short-message.vue` 中短信配置回填相关改动。
- 回滚 FEAT-0035 文档与看板状态。
