# FEAT-0044 电池列表回退操作 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-04-21
- related_feature: FEAT-0044
- version: v0.1.0

## 1. 本次变更
- 后台 `BMS 管理 > 电池列表` 生命周期菜单新增“回退”操作。
- 经销商/门店可将当前自有库存按最近一次入库来源回退给上级机构。
- 新增回退预览接口与执行接口。
- 电池运营日志新增 `ROLLBACK` 类型。

## 2. 影响范围
- `backend/` 电池生命周期服务、BMS 电池 API、权限 SQL。
- `frontend/` 电池列表、运营日志筛选、多语言文案。

## 3. 发布后验证
1. 用经销商账号验证一台来源为 PACK 的电池回退。
2. 用门店账号验证一台来源为经销商的电池回退。
3. 在运营日志页面筛选 `ROLLBACK`，确认记录和描述正确。

## 4. 回滚说明
- 回滚 FEAT-0044 对应代码与前端入口。
- 执行权限回滚时需同步移除 `bms_battery_list_action_lifecycle_rollback`。
- 已产生的 `device_org_transfers` 与 `ROLLBACK` 日志保留，不做历史数据回退。
