# FEAT-0016 遗留 BMS 设备 UUID 自动补建 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-03-17
- related_feature: FEAT-0016
- version: v0.1.0

## 1. 背景与目标
- 背景：
  - 当前移动端蓝牙添加 BMS 设备时，会先读取设备 `UUID(item_uuid)`，再调用云平台接口查询该设备是否已预置到数据库。
  - 对于云平台上线前已出货的一批遗留设备，设备本身仍可通过 BLE 协议读取 UUID，但云端不存在对应 `devices/device_batteries` 记录，导致移动端无法继续绑定。
  - 这批遗留设备不具备再由运营/后台批量补录的现实条件，需要 APP 端在首次绑定时由后端自动补建最小设备档案。
- 目标：
  1. 当移动端读取到 UUID 后，若云端无对应记录且满足策略，允许后端自动补建该设备。
  2. 自动补建与绑定在同一事务中完成，避免出现“已建档但未绑定”的半成品数据。
  3. 自动补建记录需保留来源标识，便于后续筛选、审计和回滚。

## 2. 范围
### In Scope
- 调整 APP 设备开通查询接口返回结构，支持表达“设备不存在但允许自动补建”。
- 调整 APP 设备开通绑定接口，在查无记录时按策略自动创建 `devices` 与 `device_batteries` 占位记录。
- 新增后端配置项控制是否允许遗留设备自动补建。
- UniApp 开通向导支持“可自动补建”分支提示与继续绑定。
- 文档、看板、实现日志、测试报告同步更新。

### Out of Scope
- 不根据 UUID 自动推断 `product_id`、`device_config_id`、电池型号、组织归属等扩展业务字段。
- 不新增后台手工“遗留设备补录”页面。
- 不改变现有 BLE 协议、UUID 读取指令或设备端固件行为。
- 不开放给后台通用设备创建接口复用本逻辑。

## 3. 用户价值
- 遗留出货设备无需提前在云端建档，也能由终端用户通过蓝牙完成首次添加。
- 平台保留设备来源与自动补建痕迹，后续客服、运营可定位这类特殊设备。
- 保持当前 BLE 开通主流程不变，前端改动小，实施风险低。

## 4. 验收标准
1. 当 `item_uuid` 已存在于当前租户下时，移动端开通和绑定行为与现状一致。
2. 当 `item_uuid` 不存在且配置允许自动补建时：
   - `GET /api/v1/app/device/provision/info` 返回 `exists=false`、`can_auto_register=true`。
   - `POST /api/v1/app/device/provision/bind` 可在同一事务内完成自动补建与绑定。
3. 自动补建的设备满足以下最小数据要求：
   - `devices.device_number = item_uuid`
   - `devices.tenant_id = 当前租户`
   - `devices.remark1/remark2` 或 `additional_info` 中可识别“移动端自注册/APP_BLE”
   - `device_batteries.item_uuid = item_uuid`
   - `device_batteries.bms_comm_type = 1`
4. 当并发请求同时对同一 `item_uuid` 触发自动补建时，不产生重复设备记录。
5. 当配置关闭自动补建时，查询不到设备仍按现有口径拒绝绑定。
6. 移动端在“可自动补建”场景下显示明确提示，并继续完成绑定。

## 5. 风险与约束
- 若不加策略开关，任意兼容协议设备都可能通过 APP 往租户下写入占位设备，存在脏数据风险。
- `devices.device_number` 为全局唯一，跨租户同 UUID 抢注册会触发唯一约束；需明确冲突提示。
- 自动补建设备缺少 `product_id/device_config_id` 等信息，后台部分依赖这些字段的功能可能需要后续补录。
- 现有 `GET provision/info` 已被前端当成“存在性校验”使用，改返回结构时要兼容旧分支。

## 6. 回滚方案
- 回滚 UniApp 开通向导的“可自动补建”提示与继续绑定逻辑。
- 回滚后端 `provision/info` 返回扩展字段和 `bind` 中的自动补建逻辑。
- 配置层将自动补建开关关闭，作为紧急止血手段。
- 若需清理已自动补建数据，可按 `remark2=BLE_UUID_AUTO_REGISTER` 或 `additional_info.auto_registered=true` 筛选后人工核对处理。
