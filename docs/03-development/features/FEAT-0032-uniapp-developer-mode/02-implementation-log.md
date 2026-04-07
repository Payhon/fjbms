# FEAT-0032 UniApp 开发者模式 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-03 01:20
- related_feature: FEAT-0032
- version: v0.1.0

## 1. 实施记录
1. 新建 FEAT-0032 功能文档目录，并补齐规格、设计、实施、测试、发布五件套。
2. 梳理 `fjbms-uniapp` 登录页现状，确认顶部品牌 LOGO 与登录卡片结构可直接承载入口与调试信息展示区。
3. 梳理现有运行时配置获取方式，确认 `resolveBaseUrl()` 已与当前请求逻辑保持一致，可直接复用为调试展示值。
4. 规划开发者模式状态采用 Pinia + `uni.setStorageSync` 持久化实现，并向 legacy `$store.state` 暴露只读布尔值，便于历史页面后续复用。
5. 规划版本号读取逻辑：
   - 优先使用 `uni.getAppBaseInfo()` / `uni.getSystemInfoSync()` 获取应用版本与 uni 运行时版本；
   - APP 场景下再用 `plus.runtime` 做兜底，避免字段缺失。
6. 已新增 `useDeveloperStore()`：
   - 通过 `__developer_mode_enabled__` 本地存储键持久化开发者模式。
   - 同时向 legacy `$store.state` 暴露 `developerMode`，便于历史页面后续复用。
7. 已新增 `common/app-debug.ts`：
   - 统一输出 `baseVersion`、`appVersion`、`apiBaseUrl`。
   - API 地址直接复用 `resolveBaseUrl()`，确保展示值与真实请求一致。
8. 已完成登录页改造：
   - 顶部 LOGO 支持连续点击 9 次开启开发者模式。
   - 单次点击间隔超过 1.5 秒自动重置计数。
   - 开发者模式下在登录卡片底部展示基座版本号、应用版本号与 API BaseURL。
9. 已完成中英文文案补充：
   - 新增开发者模式标题、开启提示和调试字段标签。

## 2. 待执行项
- APP / 小程序运行态验收记录补充。
- 根据验收结果决定是否切换到 `review`。

## 3. 当前状态
- 文档已进入 `in_progress`。
- 代码实现与静态校验已完成，当前待运行态验收。
