# FEAT-0042 电池出厂增强与跨页批量选择 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-17
- related_feature: FEAT-0042
- version: v0.1.0

## 1. 方案概览
- OpenAPI 电池建档请求新增 `pack_factory_name`。
- 建档成功后，按当前租户 `orgs(name, org_type=PACK_FACTORY)` 做精确匹配；唯一命中时复用现有 `FactoryOutBattery` 完成自动出厂。
- 新增 `POST /api/v1/battery/batch-factory-out`，批量逐台复用单条出厂逻辑，返回汇总结果。
- 前端电池列表把勾选状态拆成：
  - `selectedRowKeys`：跨页保留已选主键；
  - `selectedRowsMap`：缓存已选设备摘要信息，供批量弹窗展示。

## 2. 接口与数据结构
### 2.1 OpenAPI
- `POST /api/v1/openapi/mes/battery`
  - 请求新增：
    - `pack_factory_name?: string`
  - 行为：
    - 空值：仅建档。
    - 唯一匹配：建档后自动出厂。
    - 未匹配/非唯一：建档成功，自动出厂跳过。

### 2.2 后台批量出厂接口
- 新增 `POST /api/v1/battery/batch-factory-out`
  - 请求：
    - `device_ids: []string`
    - `to_org_id: string`
    - `remark?: string`
  - 响应：
    - `total`
    - `success`
    - `failed`
    - `failures[]`

## 3. 关键流程
1. 第三方调用 OpenAPI 建档。
2. 后端完成设备/电池扩展信息写入。
3. 若传了 `pack_factory_name`，查询当前租户下唯一 PACK 厂家。
4. 唯一命中时，调用单条出厂服务写入 `device_batteries.owner_org_id`、转移记录与运营日志。
5. 后台批量出厂时，前端从跨页勾选集合取 `device_ids` 提交批量接口。
6. 后端逐台执行单条出厂校验与事务写入，汇总失败原因返回前端。

## 4. 权限与兼容
- 新增前端按钮权限：
  - `bms_battery_list_batch_factory_out`
- `PACK_FACTORY` 权限模板补齐该按钮。
- 批量出厂只扩展后台 BMS 管理页面，不影响现有单条出厂、调拨、激活逻辑。

## 5. 测试策略
- 后端：
  - OpenAPI：空值/唯一命中/未命中/重复命中。
  - 批量出厂：全部成功、部分成功、无权限、设备不在厂家库存。
- 前端：
  - 第 1 页选择 + 第 2 页继续选择 + 返回上一页取消。
  - 批量信息补全/批量出厂共用跨页勾选结果。
