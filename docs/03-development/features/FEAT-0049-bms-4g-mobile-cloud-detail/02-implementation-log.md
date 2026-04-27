# FEAT-0049 BMS 4G 移动端云端详情链路 - 实现日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-27
- related_feature: FEAT-0049
- version: v0.1.0

## 2026-04-27
1. 新增 APP 当前遥测接口
   - `GET /api/v1/app/battery/current-telemetry/:device_id`
   - 返回当前遥测键、最后上报时间、在线状态和可解析的 `bms.snapshot`
2. 调整 UniApp 设备详情连接策略
   - 4G-only 设备跳过 BLE/MQTT 主动读链路
   - 使用云端当前遥测合成详情页 `BmsStatus`
   - 保留 BLE-only 设备原逻辑
3. 优化电芯 Tab 空态
   - 未收到 `cell.voltagesMv` 时显示“未收到电芯明细数据”
   - 不根据最高/最低/压差摘要伪造单体列表
4. 修复 4G 动态电芯帧到当前遥测的结构化链路
   - `bms-bridge` 在 `report.startAddress == 0x0141` 时基于已知 `seriesCount`、`cellTempCount` 解析动态区。
   - 新增输出 `cell.voltagesMv`、`temperature.cellTempsC`、最高/最低单体电压索引、单体电压和、平均单体电压等扁平字段。
   - 元数据优先来自 `0x0100` 完整状态帧缓存，缓存缺失时回查当前遥测/属性；仍缺失则只保留原始寄存器，不猜测数组边界。
   - 局部动态区帧不生成 `bms.snapshot`，避免覆盖完整状态快照。
5. 更新后台 BMS 面板云端展示
   - 当前遥测订阅键增加 `cell.voltagesMv`、`temperature.cellTempsC`、`electrical.cellVoltageIndex.*` 等字段。
   - 电芯 Tab 在无 `bms.snapshot.cell.voltagesMv` 时回退使用当前遥测 `cell.voltagesMv`。
   - 支持复杂遥测值以 JSON 字符串落库后的数组解析。
6. 明确数据源差异
   - 通讯调试管理读取 `bms_bridge_comm_logs` 原始报文链路。
   - 后台/移动端 BMS 面板读取当前遥测和可选 `bms.snapshot`，需要 bridge 规则发布结构化字段后才可展示电芯列表。
