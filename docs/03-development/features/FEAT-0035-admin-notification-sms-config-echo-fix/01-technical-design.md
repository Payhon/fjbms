# FEAT-0035 后台通知设置短信配置回显修复 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-04-07
- related_feature: FEAT-0035
- version: v0.1.0

## 1. 问题定位
- 短信配置页当前回填逻辑仅执行 `Object.assign(formModel, data)`，然后尝试直接用 `JSON.parse(data.config)` 整体替换 `formModel.sme_config`。
- 该实现缺少两层保护：
  - 未统一处理接口响应是否已被请求层解包。
  - 未按字段级合并默认短信配置，导致页面在解析失败、响应结构不完整或嵌套对象替换不稳定时，只保留默认值，未能把 `config` 中实际配置回显到表单。

## 2. 设计方案
### 2.1 标准化响应解包
- 增加 `resolveNotificationConfigPayload`，兼容两类输入：
  - 请求层已返回业务对象。
  - 调用方拿到包含 `data` 字段的包裹对象。

### 2.2 标准化短信配置解析
- 增加 `createDefaultSMSConfig()` 统一维护短信配置默认值。
- 增加 `normalizeSMSConfig()`：
  - 优先解析 `config` 字段中的 JSON 字符串。
  - 若 `config` 不可用，则回退使用 `sme_config`。
  - 最终使用字段级 `Object.assign` 合并到默认结构中，保证缺省字段稳定。

### 2.3 保留响应式嵌套对象
- `setTableData()` 不再整对象替换 `formModel.sme_config`。
- 改为逐字段更新顶层表单数据，并对 `aliyun_sms_config` 做字段级合并，保持表单绑定引用稳定。

## 3. 接口与数据结构
- 读取接口：`GET /notification/services/config/SME_CODE`
- 关键数据结构：
  - 顶层：`id`、`config`、`notice_type`、`status`、`remark`
  - `config` JSON：`provider`、`aliyun_sms_config.access_key_id`、`access_key_secret`、`endpoint`、`sign_name`、`template_code`

## 4. 安全与权限
- 本次改动仅影响前端展示与回填逻辑，不新增权限点。
- 不改变已有敏感字段传输方式。

## 5. 测试策略
- 静态验证：执行 `pnpm --dir frontend typecheck`。
- 运行态验证：
  1. 打开通知设置短信页。
  2. 确认接口返回的阿里云短信参数已回显。
  3. 修改后保存，再次刷新页面确认值仍正常显示。

## 6. 兼容性与迁移
- 不涉及数据库迁移。
- 不涉及后端接口升级。
- 与现有仅支持 `ALIYUN` 的短信服务商实现兼容。
