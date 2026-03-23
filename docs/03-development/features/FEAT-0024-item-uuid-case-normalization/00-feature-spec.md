# FEAT-0024 item_uuid 大小写归一化防重复注册 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-03-23
- related_feature: FEAT-0024
- version: v0.1.0

## 1. 背景与目标
- 背景：
  - 当前 UniApp 蓝牙开通流程会先读取 BMS 板 `UUID(item_uuid)`，再调用后端 `provision/info` 与 `provision/bind`。
  - BLE 协议层当前返回的小写 16 进制字符串可能与云端数据库中统一按大写存储的 `item_uuid` 不一致。
  - PostgreSQL 对普通字符串 `=` 比较默认区分大小写，导致同一设备在“库中已有大写记录、客户端传入小写 UUID”时被误判为不存在，进而触发自动补建，形成大小写不同的重复设备。
- 目标：
  1. 将移动端 `item_uuid` 在进入后端前统一归一化为大写。
  2. 将后端 `provision` 链路的 `item_uuid` 查询与写入统一使用大写规范值，避免再次产生大小写重复。
  3. 在不引入数据库结构变更的前提下，兼容历史上可能已存在的小写 `item_uuid` 记录。

## 2. 范围
### In Scope
- UniApp BLE `readUuid()` 返回值改为大写十六进制。
- UniApp `deviceProvision` 接口请求前对 `item_uuid` 做统一大写归一化。
- 后端 `device_provision` 查询、自动补建、绑定链路统一对 `item_uuid` 做大写归一化。
- 后端查询在必要时兼容历史小写记录，避免旧脏数据继续影响绑定。
- 文档、实现日志、测试报告、发布说明、看板同步更新。

### Out of Scope
- 不修改其他与 `item_uuid` 无关的业务接口。
- 不新增数据库字段、不新增函数索引、不执行历史数据清洗脚本。
- 不调整 BLE 协议本身，只调整客户端/服务端字符串归一化策略。

## 3. 验收标准
1. 当数据库中已存在大写 `item_uuid` 设备记录时，移动端传入同值小写 UUID，`provision/info` 能正确命中已有设备。
2. 当移动端通过 BLE 读取 UUID 后，发往后端的 `item_uuid` 为大写 32 位十六进制字符串。
3. `provision/bind` 自动补建时写入的 `devices.device_number` 与 `device_batteries.item_uuid` 统一为大写。
4. 历史存在的小写 `item_uuid` 记录时，查询链路仍可按大小写无关方式命中，避免再次补建重复记录。
5. 本次改动不影响已预置设备绑定、UUID 扫码绑定、遗留设备自动补建等既有流程。

## 4. 风险与约束
- 若只改前端，不改后端，仍可能被旧客户端或其他调用方以小写 UUID 绕过。
- 若只改后端查询而不改写入规范，未来仍可能继续产生大小写混用数据。
- 使用 SQL 大小写无关匹配可兜底历史脏数据，但不是主规范；主规范仍应是“统一存大写、统一查大写”。

## 5. 回滚方案
- 回滚 UniApp `UUID/item_uuid` 大写归一化改动。
- 回滚后端 `device_provision` 中的 `item_uuid` 归一化与兼容查询逻辑。
- 若回滚后需临时止血，可关闭遗留设备自动补建开关，避免查询误判时继续创建重复设备。
