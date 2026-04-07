# FEAT-0034 后台存储设置访问域名输入修复 - 功能规格

- status: review
- owner: payhon
- last_updated: 2026-04-03
- related_feature: FEAT-0034
- version: v0.1.0

## 1. 背景与目标
- 背景：
  - 后台管理 `系统管理 > 系统设置 > 存储设置` 切换到云存储并选择阿里云 OSS 后，`访问域名 / CDN域名` 输入框在最新前后端版本下仍无法正常录入。
  - 保存请求发出时，`aliyun.domain` 仍为空字符串，后端因此返回 `aliyun config incomplete`。
- 目标：
  1. 修复前端存储设置页阿里云域名字段无法录入的问题。
  2. 保证用户输入的 `aliyun.domain` 能正确保存在表单模型中并提交到后端。
  3. 不改变现有存储设置接口结构与后端校验逻辑。

## 2. 范围
### In Scope
- `frontend/src/views/management/setting/components/storage-setting.vue`
- 表单配置回填逻辑修复。
- 保存请求前的表单数据序列化处理。
- 文档与看板同步回写。

### Out of Scope
- 不调整后端 `file/storage/config` 接口字段定义。
- 不放宽后端对云存储 `domain` 的必填校验。
- 不新增新的存储服务商或存储配置字段。

## 3. 用户价值
- 系统管理员可以正常填写阿里云 OSS 的访问域名 / CDN 域名。
- 保存云存储配置时不再因前端未写入 `domain` 而直接失败。

## 4. 验收标准
1. 在存储设置页面选择 `云存储 > 阿里云 OSS` 后，`访问域名 / CDN域名` 输入框可正常输入内容。
2. 输入域名后点击保存，请求体中的 `aliyun.domain` 与界面输入值一致。
3. 现有本地存储、七牛云配置编辑行为不受影响。
4. 本次改动不引入 TypeScript 编译错误。

## 5. 风险与约束
- 存储设置表单包含多层嵌套对象，若直接整对象替换响应式子对象，存在表单输入状态异常风险。
- 需要兼容已有密钥占位逻辑，不能在修复域名输入时破坏 `access_key_secret_set` / `secret_key_set` 的现有行为。

## 6. 回滚方案
- 回滚 `storage-setting.vue` 中表单回填与提交相关改动。
- 回滚 FEAT-0034 文档与看板状态。
