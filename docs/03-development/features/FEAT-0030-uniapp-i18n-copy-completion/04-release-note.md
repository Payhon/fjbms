# FEAT-0030 UniApp 页面多语言文案补全 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-04-02
- related_feature: FEAT-0030
- version: v0.1.0

## 1. 变更摘要
- 补齐 UniApp 首页、设备详情及常用页面的多语言文案调用。
- 新增中英文词条，减少页面语言切换后的硬编码残留。
- 同步清理通用提示模块中的硬编码 toast / modal 文案。

## 2. 发布关注点
- 需重点回归首页、设备详情、“我的”页及设备添加相关流程。
- 需在中文、英文两种语言下检查关键页面是否存在 key 原样透出。

## 3. 回滚说明
- 如发现页面文案异常，可回滚 FEAT-0030 相关 UniApp 提交与字典变更。
