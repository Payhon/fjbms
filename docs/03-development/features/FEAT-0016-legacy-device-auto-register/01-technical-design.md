# FEAT-0016 遗留 BMS 设备 UUID 自动补建 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-17
- related_feature: FEAT-0016
- version: v0.1.0

## 1. 方案概览
- 总体策略：保持 `provision/info` 为只读查询接口，真正的自动补建动作仅发生在 `provision/bind`。
- 后端实现：
  - `GetProvisionInfo`：查到则返回设备信息；查不到时根据配置返回 `exists/can_auto_register`。
  - `BindByItemUUID`：在事务内执行“查找 -> 需要时自动补建 -> 绑定/添加”。
- 移动端实现：
  - 查询返回 `exists=false && can_auto_register=true` 时，不再直接报“设备不存在”，而是提示将按遗留设备自动注册后继续绑定。

## 2. 接口与数据结构
### 2.1 `DeviceProvisionInfoResp`
- 新增字段：
  - `exists: bool`
  - `can_auto_register: bool`
  - `auto_register_reason?: string`
- 兼容保留字段：
  - `device_id`
  - `device_number`
  - `device_name`
  - `ble_mac`
  - `comm_chip_id`
  - `bms_comm_type`
  - `is_bound`

### 2.2 自动补建设备默认字段
- `devices`
  - `device_number = item_uuid`
  - `name = BMS-<UUID后8位>`
  - `tenant_id = claims.tenant_id`
  - `voucher = 随机默认值`
  - `protocol = BLE`
  - `is_enabled = enabled`
  - `activate_flag = inactive`
  - `access_way = A`
  - `remark1 = 移动端自注册`
  - `remark2 = BLE_UUID_AUTO_REGISTER`
  - `description = 遗留设备由APP蓝牙读取UUID后自动补建`
  - `additional_info.auto_registered = true`
- `device_batteries`
  - `device_id`
  - `item_uuid`
  - `ble_mac`（若本次读取到）
  - `bms_comm_type = 1`
  - `activation_status = INACTIVE`
  - `transfer_status = FACTORY`
  - `updated_at = now`

### 2.3 配置项
- 新增：
  - `bms.provision.allow_legacy_auto_register: false`
- 首版先采用全局开关，不做租户白名单；若后续需要再扩展。

## 3. 关键流程
1. UniApp 读取设备 UUID、硬件型号、板码和 BLE MAC。
2. 调用 `GET provision/info?item_uuid=...`
3. 若：
   - `exists=true`：按现有逻辑继续。
   - `exists=false && can_auto_register=true`：前端提示并继续。
   - 其它情况：报错退出。
4. 调用 `POST provision/bind`
5. 后端事务内：
   - 查询 `tenant_id + item_uuid`
   - 若不存在且允许自动补建，则插入 `devices` 和 `device_batteries`
   - 若并发下触发唯一约束，则回查已创建记录
   - 继续执行现有绑定/机构添加逻辑

## 4. 安全与权限
- 仅 APP 设备开通链路可触发，不扩散到后台通用创建设备入口。
- 自动补建受 `bms.provision.allow_legacy_auto_register` 开关控制。
- 设备来源写入备注/附加信息，便于审计。
- 保留现有 `ble_mac` 一致性校验，防止已存在设备被错误覆盖。

## 5. 测试策略
- 后端单元/集成验证：
  - 已存在设备查询与绑定
  - 不存在但允许自动补建
  - 不存在且不允许自动补建
  - 并发补建唯一约束冲突回查
  - `ble_mac` 补写与不一致拒绝
- UniApp 联调验证：
  - 遗留设备提示文案
  - 自动补建后绑定成功
  - 失败态信息回显

## 6. 兼容性与迁移
- 不新增数据库结构字段，优先复用 `remark1/remark2/description/additional_info`。
- 返回结构增加新字段，不移除旧字段，兼容现有调用方。
- 若旧前端未识别新字段，仍可能按 `404` 口径失败，但不会影响后端数据一致性。
