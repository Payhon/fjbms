# FEAT-0012 电芯品牌与电池型号管理（租户维度）- 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-09
- related_feature: FEAT-0012
- version: v0.1.0

## 1. 数据模型
### 1.1 电芯品牌表 `battery_cell_brands`
- `id varchar(36) PK`
- `tenant_id varchar(36) NOT NULL`
- `seq_no smallint NOT NULL CHECK (seq_no BETWEEN 1 AND 255)`
- `name varchar(16) NOT NULL`
- `created_at/updated_at timestamptz`
- 唯一约束：`(tenant_id, seq_no)`、`(tenant_id, name)`

### 1.2 BMS 板型号表 `battery_bms_models`（由历史表重命名）
- 来源：历史 `battery_models` 改名。
- 用途：租户管理员维护 BMS 板型号（保留旧字段：设备模板、额定参数等）。
- 管理接口：`/api/v1/battery/bms-model`（租户维度 CRUD）。

### 1.3 电池型号表 `battery_models`（新建）
- 字段：
  - `id varchar(36) PK`
  - `seq_no smallint`（1~255，可空用于历史兼容）
  - `name varchar(64) NOT NULL`
  - `org_id varchar(36)`（机构ID，组织账号写入）
  - `tenant_id varchar(36) NOT NULL`
  - `created_at/updated_at timestamptz`
- 索引/唯一约束：
  - `(tenant_id, org_id, seq_no)`（`org_id`/`seq_no` 非空时唯一）
  - `(tenant_id, org_id, name)`（`org_id` 非空时唯一）

## 2. 后端接口
1. 电芯品牌：`/api/v1/battery/cell-brand`
   - `GET` 列表（全量，无分页）
   - `POST` 新增
   - `PUT /:id` 更新
   - `DELETE /:id` 删除
2. 电池型号：复用 `/api/v1/battery/model`
   - 维持现有路径，改造入参与返回结构，支持机构隔离与简化字段。
3. BMS 型号：`/api/v1/battery/bms-model`
   - `GET` 列表（分页）
   - `GET /:id` 详情
   - `POST` 新增
   - `PUT /:id` 更新
   - `DELETE /:id` 删除

## 3. 权限与隔离
- 电芯品牌：按 `tenant_id` 隔离。
- 电池型号：按 `tenant_id + org_id` 隔离（组织用户仅能操作本机构）。
- 菜单新增：`bms_battery_cell_brand`（电芯品牌管理）。
- 既有按钮权限 `bms_battery_list_add` 文案改为“新增BMS”。

## 4. 前端实现
1. 新增页面 `bms/battery/cell-brand/index.vue`：
   - 表格内编辑，新增行/保存/取消/删除。
2. 改造 `bms/battery/model/index.vue`：
   - 去掉查询+分页+弹窗，改为全量表格行内编辑。
3. 电池列表页面按钮文案改为“+ 新增 BMS”。
4. 新增页面 `bms/battery/bms-model/index.vue`：
   - 菜单：`bms_battery_bms_model`
   - 用于租户管理员维护 `battery_bms_models`。

## 5. 测试策略
- 后端：`go test ./...`（重点覆盖新增 API 编译与核心服务逻辑）。
- 前端：`pnpm typecheck` + `pnpm lint`。
- 手工：
  1) 租户管理员创建/编辑/删除电芯品牌。
  2) PACK 厂家创建/编辑/删除本机构电池型号。
  3) 电池列表确认按钮文案“新增 BMS”。
