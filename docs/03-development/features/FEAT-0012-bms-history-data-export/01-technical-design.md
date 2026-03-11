# FEAT-0012 BMS 历史数据查询与异步导出通知 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-03-09
- related_feature: FEAT-0012
- version: v0.1.0

## 1. 总体方案
- 后端新增统一历史查询域：按设备聚合 `telemetry_datas` 与 `attribute_history_datas`。
- 查询接口支持 `view_mode=long|wide`：
  - `long`：按“时间 + 数据类型 + 标识符 + 值”返回行。
  - `wide`：按“时间行 + 动态 key 列”返回行与列定义。
- 导出采用异步任务表 `bms_history_export_jobs`，后台 goroutine 生成 Excel 文件。
- 导出成功后通过用户维度 WebSocket 通道推送消息，前端消息中心展示“已完成未下载”任务。

## 2. 后端设计
### 2.1 数据表
1. `attribute_history_datas`
   - 作用：属性历史明细（append-only）。
   - 索引：`(tenant_id, device_id, ts DESC)`、`(tenant_id, device_id, key, ts DESC)`。
2. `bms_history_export_jobs`
   - 字段：任务状态、查询条件快照（device/view_mode/time）、文件信息、过期时间、下载时间。
   - 索引：`(tenant_id, creator_user_id, status, downloaded_at)`、`(tenant_id, created_at DESC)`。

### 2.2 属性入库链路
- 在 `internal/storage/direct_writer.go` 中：
  - 保留 `attribute_datas` 最新值 upsert。
  - 同步追加一条 `attribute_history_datas` 记录。

### 2.3 接口
挂载前缀：`/api/v1/battery`
1. `GET /history/devices`：设备筛选列表（分页/关键字）。
2. `GET /history`：历史查询（`device_id/view_mode/start_time/end_time/page/page_size`）。
3. `POST /history/export`：创建异步导出任务。
4. `GET /history/export/jobs/pending`：已完成未下载任务列表。
5. `GET /history/export/download?task_id=...`：固定下载路由。
6. `GET /history/export/ws`：导出通知 WebSocket。

### 2.4 WebSocket
- 新增用户维度 WS 管理器（Redis PubSub + 本地连接池）。
- 推送事件：`bms_history_export_complete`，包含 `task_id/file_name/download_url/finished_at`。
- 通知范围：仅任务创建人 `creator_user_id`。

### 2.5 安全与隔离
- 统一基于 `claims.tenant_id` + 组织子树过滤设备范围。
- 下载任务需校验任务归属（租户/创建人）。
- 查询/导出均校验时间跨度不超过 31 天。

## 3. 前端设计
1. 新增页面：`/bms/battery/history`（`view.bms_battery_history`）。
2. 页面布局：左筛选（设备列表 + 搜索 + 可折叠）/右查询区（日期、视图切换、导出、表格、分页）。
3. 长宽表：
   - 长表固定列。
   - 宽表根据后端 `columns` 动态渲染。
4. 全局消息中心：
   - 顶部右上角新增消息图标（位于语言切换前）。
   - 未读闪烁，点击 Popover 展示“已完成未下载”任务表。
   - 点击下载后调用固定下载接口并移除任务行。
5. WS 连接：token query 方式连接导出通知通道，断线自动重连，进入页面/登录后可恢复任务列表。

## 4. 兼容与发布
- 数据层新增历史表不影响现有属性读取逻辑。
- 导出任务为增量功能，不影响电池列表已有导出。
- 需要执行 SQL 补丁并发布前后端同版本。
