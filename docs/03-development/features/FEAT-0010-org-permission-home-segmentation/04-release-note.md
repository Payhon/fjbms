# FEAT-0010 机构菜单权限生效与首页分层改造 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-03-07
- related_feature: FEAT-0010
- version: v0.1.0

## 1. 发布内容
- 修复机构类型菜单权限生效。
- 首页按用户类型分层展示。
- 新增接口：`GET /api/v1/dashboard/home/summary`。

## 2. 升级步骤
1. 发布后端。
2. 发布前端。
3. 使用 4 类账号回归菜单与首页。

## 3. 回归建议
- 菜单权限：分别为 `PACK_FACTORY/DEALER/STORE/APP_USER` 配置差异菜单并验证登录效果。
- 首页展示：
  - 机构账号：验证总数、状态统计、近7天/30天激活曲线。
  - 终端用户：验证“我的电池总数”显示。

## 4. 回滚
- 回滚 FEAT-0010 前后端版本。
