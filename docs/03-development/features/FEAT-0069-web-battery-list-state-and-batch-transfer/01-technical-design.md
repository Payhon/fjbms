# FEAT-0069 Web 电池列表状态记忆与批量调拨 - 技术设计

- status: approved
- owner: payhon
- last_updated: 2026-07-24
- related_feature: FEAT-0069
- version: v0.1.0

## 1. 方案概览
- 电池列表使用类型化 `sessionStorage` 保存最后一次已执行的查询快照，不缓存整个 Vue 页面实例。
- 页面在创建 `useTable` 前读取快照并构造初始查询参数，避免默认请求与恢复请求竞争。
- 批量调拨复用现有跨分页 `selectedRowKeys` / `selectedRowsMap`，后端逐台复用单台调拨校验和事务。
- 新增独立页面元素权限，不改变现有单台调拨接口。

## 2. 接口与数据结构
### 2.1 查询状态
- Session key：`bmsBatteryListSearchState`
- 内容：
  - `form`：最后一次已执行查询对应的筛选表单。
  - `apiParams`：归一化后的列表 API 参数。
  - `showAdvancedSearch`：高级筛选展开状态。
  - `page` / `pageSize`：服务端分页状态。
- 写入时机：执行查询、分页变化、每页条数变化、高级筛选展开状态变化。
- 清理时机：重置查询、退出登录、认证失效或账号切换。

### 2.2 批量调拨
- `POST /api/v1/battery/batch-transfer`
- 请求：
  - `device_ids: []string`
  - `to_org_id: string`
  - `remark?: string`
- 响应：
  - `total`
  - `success`
  - `failed`
  - `failures[]: { device_id, device_number, message }`
- 服务端按首次出现顺序去重 `device_ids`，`total` 统计唯一设备。

## 3. 关键流程
1. 页面同步读取查询快照，校验结构后恢复表单、分页和初始 API 参数。
2. `useTable` 仅用恢复后的参数发起首次请求；若保存了归属机构类型，挂载后补载机构选项。
3. 用户执行新查询时清空跨页选择、更新列表并覆盖查询快照。
4. 用户批量调拨时选择目标类型、目标机构和备注，提交跨页唯一设备 ID。
5. 后端为每台设备执行独立调拨事务并汇总结果。
6. 前端刷新列表；全部成功清空选择，部分成功仅保留响应中的失败设备。

## 4. 安全与权限
- 新增 `bms_battery_list_batch_transfer` 页面元素权限。
- 批量接口复用 FEAT-0045 的调拨矩阵、租户隔离、操作机构范围和目标组织树校验。
- 门店账号即使绕过前端调用接口也会逐台失败。
- Session 查询状态不包含 token、用户资料或电池勾选数据。

## 5. 测试策略
- 后端使用内存 SQLite 覆盖去重、全部成功、部分成功、全部失败、角色矩阵、跨租户和组织树限制。
- 前端执行定向 ESLint、TypeScript 类型检查和生产构建。
- 浏览器人工覆盖切页/刷新恢复、重置/退出清理、跨分页选择和批量调拨结果处理。

## 6. 兼容性与迁移
- 不涉及数据库表结构变更。
- 新增幂等权限迁移 `backend/sql/64.sql`，并同步基线 `backend/sql/1.sql`。
- `POST /api/v1/battery/transfer` 保持原请求和响应不变。
