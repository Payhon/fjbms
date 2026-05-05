# FEAT-0050 电池列表新增“恢复出厂”操作 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-28
- related_feature: FEAT-0050
- version: v0.1.0

## 2026-04-28
1. 后端新增 `BatteryFactoryRestoreReq` 与接口 `POST /api/v1/battery/factory_restore`。
2. 在电池生命周期服务实现 `FactoryRestoreBattery(...)`：
   - 权限复用出厂口径；
   - 恢复目标写 `owner_org_id = NULL`；
   - 写 `device_org_transfers(to_org_id=NULL)`；
   - 写 `battery_operation_logs(operation_type=FACTORY_RESTORE)`。
3. 前端电池列表新增生命周期“恢复出厂”入口、确认弹窗、提交流程。
4. 运营日志筛选新增 `FACTORY_RESTORE`。
5. 补充权限与多语言：
   - `backend/sql/53.sql`
   - `backend/sql/1.sql`
   - `frontend/src/locales/langs/zh-cn/route.json`
   - `frontend/src/locales/langs/en-us/route.json`

## 2026-04-29
1. 修正前端“恢复出厂”入口显隐条件，改为与后端权限口径一致：
   - 厂家组织账号可见；
   - 无组织的 `TENANT_ADMIN / SYS_ADMIN` 也可见。
