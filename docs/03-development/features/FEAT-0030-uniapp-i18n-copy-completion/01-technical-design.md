# FEAT-0030 UniApp 页面多语言文案补全 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-02
- related_feature: FEAT-0030
- version: v0.1.0

## 1. 设计概述
- 延续项目现有 `vue-i18n` 接入方式：
  - 模板中使用 `$t('...')`
  - `script setup` / Composition API 中使用 `const { t } = useI18n()`
  - 非 Vue 模块使用 `i18n.global.t(...)`
- 改造策略按页面分区推进：先首页，再设备详情，最后其他页面与通用模块。
- 字典统一收口到 `fjbms-uniapp/lang/zh-CN.ts` 与 `fjbms-uniapp/lang/en-US.ts`，按页面域增加命名空间，避免散落。

## 2. 命名约定
- 页面级 key 优先挂在 `pages.*` 下，例如：
  - `pages.home.xxx`
  - `pages.deviceDetail.xxx`
  - `pages.my.xxx`
- 通用运行时提示优先复用 `common.*` 或新增 `common.toast.*` / `common.update.*`。
- 保持已有 key 不做破坏式重命名，仅新增缺失项并在新代码中引用。

## 3. 具体实现
### 3.1 首页
- 清理首页筛选、空态、按钮、设备卡片菜单等硬编码文案。
- 首页组件内通过 `useI18n()` 注入 `t`，避免在父层预拼接所有文本。

### 3.2 设备详情
- 针对 `detail.vue` 与子组件中卡片标题、状态标签、空态、操作提示做替换。
- 协议枚举与动态状态文本保持映射逻辑不变，仅将展示值改为国际化 key。

### 3.3 其他页面与通用模块
- “我的”、告警、通知详情、机构设备页优先处理用户可感知文案。
- `common/request.ts`、`common/util.ts` 中的 `showToast` / `showModal` 文案统一切换到 `i18n.global.t(...)`。

## 4. 验证方案
- 执行 TypeScript 静态校验，确认新引入的 `useI18n` / `i18n` 调用无编译错误。
- 抽样检查首页、设备详情、“我的”页的模板与脚本，确认不存在明显硬编码残留。
- 人工比对 `zh-CN` / `en-US` 字典项是否成对新增。

## 5. 不兼容变更评估
- 本次仅替换展示层文案调用，不涉及接口协议、数据结构和页面路由，因此无外部不兼容变更。
