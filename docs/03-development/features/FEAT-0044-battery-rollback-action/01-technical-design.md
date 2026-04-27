# FEAT-0044 电池列表回退操作 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-23
- related_feature: FEAT-0044
- version: v0.1.0

## 1. 方案概览
- 在 `backend/internal/service/battery_lifecycle.go` 新增一套共享的回退解析逻辑：
  - 读取当前设备、电池归属、当前机构、直系上级机构（`parent_id`）。
  - 校验操作者必须是当前持有机构，且机构类型仅允许 `DEALER/STORE`。
  - 校验上级机构类型与组织树关系合法：
    - 经销商上级必须是 `PACK_FACTORY`
    - 门店上级允许 `DEALER/PACK_FACTORY`
  - 校验存在最近一条“来自该上级”的入库记录（`to_org_id=currentOrg` 且 `from_org_id=parentOrg`）。
- 基于同一套解析逻辑提供两个接口：
  - `GET /api/v1/battery/rollback/preview`
  - `POST /api/v1/battery/rollback`
- 前端新增独立回退弹窗，仅展示设备编号、当前机构、回退目标、备注。

## 2. 接口与数据结构
### 2.1 预览接口
- `GET /api/v1/battery/rollback/preview?device_id=...`
- 返回：
  - `device_id`
  - `device_number`
  - `current_org_id`
  - `current_org_name`
  - `rollback_to_org_id`
  - `rollback_to_org_name`
  - `can_rollback`
  - `reason`

### 2.2 执行接口
- `POST /api/v1/battery/rollback`
- 请求：
  - `device_id: string`
  - `remark?: string`
- 响应：
  - `message: "回退成功"`

### 2.3 日志
- 新增电池操作日志类型：
  - `ROLLBACK`
- 描述格式：
  - `回退：{当前机构} -> {来源机构}`

## 3. 关键流程
1. 电池列表点击“回退”。
2. 前端先调用预览接口，读取回退目标机构。
3. 若 `can_rollback=false`，前端直接提示 `reason`，不打开弹窗。
4. 用户确认后，前端提交执行接口。
5. 后端在事务内再次复用回退解析逻辑，防止预览后状态变化。
6. 更新 `device_batteries.owner_org_id`，写入新的 `device_org_transfers` 记录。
7. 写入 `battery_operation_logs(operation_type=ROLLBACK)`。

## 4. 权限与兼容
- 新增按钮权限码：
  - `bms_battery_list_action_lifecycle_rollback`
- 前端仅在 `DEALER/STORE` 账号且行归属机构类型与当前账号机构类型一致时展示入口。
- 后端不信任前端显隐，仍强制校验当前账号只能操作自己当前持有的库存。

## 5. 测试策略
- 后端：
  - 经销商回退到上级 PACK。
  - 门店回退到上级经销商或上级 PACK。
  - 非当前持有机构回退。
  - 无上级、无来自上级的入库记录、上级类型非法、链路非法。
- 前端：
  - 符合条件的经销商/门店库存显示入口。
  - 预览失败提示正确。
  - 确认弹窗无机构选择控件。
  - 回退成功后列表刷新，运营日志可筛选 `ROLLBACK`。
