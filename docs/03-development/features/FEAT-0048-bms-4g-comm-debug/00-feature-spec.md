# FEAT-0048 BMS 4G 通讯调试管理 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-04-24
- related_feature: FEAT-0048
- version: v0.1.0

## 1. 背景与目标
- 当前后台缺少面向 BMS 4G 设备的原始通讯观测入口，运维排查只能看 bridge 控制台日志，无法按设备回查。
- 本次要求明确基于 `bms-bridge` 独立命令行程序实施，不改造成全站通用 MQTT 调试平台。
- 目标：
  1. 采集 `bms-bridge` 可观测到的 4G BMS 通讯日志并落库。
  2. 在后台新增 `BMS管理 > 通讯调试管理` 页面，支持按设备查询与实时追加。
  3. 将日志保留控制在 7 天内。

## 2. 范围
### In Scope
- `bms-bridge` 采集以下日志：
  - 设备上行原始包
  - 上行 hex 解码结果
  - 上行 frame 解析结果
  - bridge 下发 telemetry / attributes / events
  - bridge 处理异常、发布异常
- 仅采集能关联到 `device_batteries` 且具备 4G 字段口径的 BMS 设备。
- 后端新增分页查询接口与 SSE 实时流接口。
- 后台新增通讯调试管理菜单与页面。
- 新增 SQL、文档和看板同步。

### Out of Scope
- 不在本期通过 `bms-bridge` 伪造 Broker 侧 MQTT 认证、连接、断开日志。
- 不改造主站通用 MQTT Adapter、设备详情通用调试页或移动端日志页。
- 不做日志导出、批量下载或长期归档。

## 3. 验收标准
1. 仅 4G BMS 设备的 `bms-bridge` 消息会进入新日志表。
2. 后台页面可按设备 ID、设备编号、事件类型、状态、时间范围查询。
3. 打开页面后，新增通讯日志可实时追加到列表顶部。
4. 明细弹窗能查看原始 payload、解析摘要、错误信息与 message_id。
5. 日志表仅保留最近 7 天数据。

## 4. 风险与约束
- 4G 设备识别必须走单一口径，避免普通 MQTT 设备误入日志表。
- 实时接口需要支持筛选条件，不能复用当前全局 SSE 广播通道。
- 高频消息写库会增加 bridge 压力，本期只做必要字段，不叠加额外聚合写入。

## 5. 回滚方案
- 回滚 `bms-bridge` 通讯日志采集代码。
- 下线后台 `通讯调试管理` 菜单与页面。
- 保留或手动清理 `bms_bridge_comm_logs` 表数据。
