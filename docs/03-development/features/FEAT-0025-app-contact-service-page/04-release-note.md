# FEAT-0025 APP 联系客服单页内容接入 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-03-25
- related_feature: FEAT-0025
- version: v0.1.0

## 1. 发布内容
- APP 内容管理单页内容新增“联系客服”。
- UniApp “我的 > 联系客服”改为展示后台发布的单页内容。
- 后端内容接口支持 `contact_service` 内容键。

## 2. 影响范围
- `backend/` APP 内容管理接口
- `frontend/` APP 管理 > 内容管理
- `fjbms-uniapp/` 我的页联系客服入口

## 3. 升级步骤
1. 部署后端与管理端代码。
2. 部署 UniApp 新版本。
3. 进入后台 `APP 管理 > 内容管理 > 单页内容`，选择“联系客服”，维护各语言内容并发布。

## 4. 回滚步骤
1. 回滚 FEAT-0025 对应前后端与 UniApp 提交。
2. 如需临时降级，可保留数据库内容但停止在前后端暴露 `contact_service` 入口。

## 5. 已知问题
- 联系客服当前仅支持单页文案展示，不包含电话、IM 或外链能力。
