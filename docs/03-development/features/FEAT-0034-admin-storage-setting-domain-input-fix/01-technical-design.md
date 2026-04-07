# FEAT-0034 后台存储设置访问域名输入修复 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-04-03
- related_feature: FEAT-0034
- version: v0.1.0

## 1. 问题定位
- 当前页面在加载配置后，使用 `Object.assign(formModel, { aliyun: data.aliyun, qiniu: data.qiniu, ... })` 直接替换嵌套配置对象。
- `storage-setting.vue` 的输入项使用 `v-model:value="formModel.aliyun.domain"` 绑定嵌套字段。
- 直接替换响应式子对象会增加表单交互异常风险，表现为域名字段输入值未稳定写回表单模型，最终请求中 `aliyun.domain` 仍为空。

## 2. 设计方案
### 2.1 保留响应式子对象
- 保留 `formModel.local`、`formModel.aliyun`、`formModel.qiniu` 原有响应式引用。
- 新增 `applyFormModel(data)`，改为对嵌套对象执行字段级 `Object.assign`：
  - `Object.assign(formModel.local, defaults.local, data?.local ?? {})`
  - `Object.assign(formModel.aliyun, defaults.aliyun, data?.aliyun ?? {})`
  - `Object.assign(formModel.qiniu, defaults.qiniu, data?.qiniu ?? {})`

### 2.2 提交前深拷贝
- 保存时先对 `formModel` 执行深拷贝，再传给 `upsertFileStorageConfig`。
- 目的：
  - 避免将响应式代理对象直接交给请求层。
  - 保持请求 payload 稳定、可预期。

## 3. 兼容性说明
- 不修改后端接口结构。
- 不改变存储设置默认值语义。
- 保留阿里云/七牛云密钥已设置标记字段。

## 4. 验证方案
- 静态验证：执行 `pnpm --dir frontend typecheck`。
- 运行态验证：
  1. 打开存储设置页。
  2. 选择阿里云 OSS。
  3. 录入 `访问域名 / CDN域名`。
  4. 点击保存，确认请求体 `aliyun.domain` 非空。
