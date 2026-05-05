# FEAT-0050 电池列表新增“恢复出厂”操作 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-04-28
- related_feature: FEAT-0050
- version: v0.1.0

## 1. 发布内容
- 电池列表生命周期新增“恢复出厂”操作。
- 厂家可将误下发到下游机构的电池恢复到厂家库存（`owner_org_id=NULL`）。
- 新增后端接口 `POST /api/v1/battery/factory_restore`。
- 运营日志新增 `FACTORY_RESTORE` 类型筛选。

## 2. 影响范围
- `backend/`：电池生命周期服务、电池 API、权限 SQL。
- `frontend/`：电池列表生命周期菜单、运营日志筛选、多语言。
- `docs/`：新增 FEAT-0050 文档与看板记录。

## 3. 发布后验证
1. 厂家账号恢复一台非厂家库存电池，验证成功并回到厂家库存。
2. 重复恢复同一台已在厂家库存电池，验证被拒绝。
3. 运营日志筛选 `FACTORY_RESTORE`，验证记录描述正确。

## 4. 回滚说明
- 回滚 FEAT-0050 代码与权限 SQL 变更。
- 历史 `device_org_transfers` 与 `FACTORY_RESTORE` 日志保留。
