# FEAT-0048 BMS 4G 通讯调试管理 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-04-24
- related_feature: FEAT-0048
- version: v0.1.0

## 1. 发布内容
- 新增 `bms_bridge_comm_logs` 通讯日志表
- 新增 BMS 后台菜单 `通讯调试管理`
- `bms-bridge` 增加 4G BMS 通讯日志采集与 7 天清理
- 后端新增分页查询接口和 SSE 实时流接口

## 2. 发布前检查
- 执行 `backend/sql/52.sql`
- 确认 `bms-bridge` 已更新到包含通讯调试日志采集的版本
- 确认后台账号拥有 `bms_ops_comm_debug` 菜单权限

## 3. 回滚说明
- 恢复旧版 `bms-bridge` 二进制
- 回滚前端通讯调试页面与菜单入口
- 如需彻底回退，可删除 `bms_bridge_comm_logs` 表及 `bms_ops_comm_debug` 菜单项
