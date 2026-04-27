# FEAT-0047 BMS 分页修复与电池详情操作记录 Tab - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-04-22
- related_feature: FEAT-0047
- version: v0.1.0

## 1. 背景与目标
- `BMS管理 > 运营管理 > 操作记录` 与 `激活日志` 当前已返回正确总数，但底部分页未按后端总数计算，导致无法翻页。
- 同类实现中还有若干 `NDataTable` 走服务端分页、却仍按本地分页渲染页码的页面，存在相同风险。
- 电池详情页在 BMS 模式下已有 `BMS面板 / 基本信息 / 连接`，缺少面向后台运维的电池生命周期操作追踪入口。
- 目标：
  1. 修复 BMS 后台已确认页面的服务端分页异常。
  2. 在电池详情页新增“操作记录”Tab，展示该电池的现有运营日志。
  3. 将该 Tab 纳入页面元素权限，默认对厂家、PACK 厂家、经销商可见。

## 2. 范围
### In Scope
- 修复以下页面的服务端分页显示：
  - `运营管理 > 操作记录`
  - `运营管理 > 激活日志`
  - `BMS 型号管理`
  - `API Key 列表`
  - `APP 用户选择弹窗`
- 后端 `GET /api/v1/battery/operation_logs` 新增 `device_id` 可选过滤参数。
- 电池详情页 BMS 模式新增 `操作记录` Tab，按 `device_id` 精确查询 `battery_operation_logs`。
- 新增页面元素权限 `perm.bms_battery_detail_operation_log`，默认放开 `BMS_FACTORY`、`PACK_FACTORY`、`DEALER`。
- 同步 SQL、locale、功能文档、测试报告与项目看板。

### Out of Scope
- 不合并通用 `operation_logs` 到电池详情操作记录。
- 不改造移动端、APP 端日志展示。
- 不对未确认存在同类缺陷的其他列表做重构。

## 3. 验收标准
1. 操作记录页与激活日志页在总数超过一页时，可以正常显示总页数并翻页。
2. 本次已确认的同类页面翻页逻辑一致，不再出现“总数很多但只有 1 页”的问题。
3. 从电池列表进入 `device_details?bms=1` 时，若用户拥有权限，则看到 `操作记录` Tab。
4. `操作记录` Tab 仅展示该 `device_id` 对应的 `battery_operation_logs`，按时间倒序分页展示。
5. 无权限用户不显示该 Tab，也不会留下空占位。
6. 权限后台可配置该新权限项，默认 PACK 厂家/经销商具备该权限。

## 4. 风险与约束
- 服务端分页页面必须显式按远程分页模式渲染，否则即使 `itemCount` 正确，页码也可能继续按当前页数据长度计算。
- `device_id` 过滤必须叠加租户与组织隔离，不能绕过现有数据权限。
- 电池详情 Tab 权限必须走现有 UI 权限体系，避免另起一套判断口径。

## 5. 回滚方案
- 回滚新增的 `device_id` 查询参数支持与详情页 Tab。
- 回滚权限补丁 `51.sql` 及 `backend/sql/1.sql` 对应汇总项。
- 回滚前端分页 `remote` 修复与详情页 Tab 装配改动。
