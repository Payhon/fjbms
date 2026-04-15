# FEAT-0041 UniApp OTA 地址口径统一与仪表会话升级支持 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-15
- related_feature: FEAT-0041
- version: v0.1.0

## 1. 方案概览
- UniApp OTA 地址统一：
  - 仪表：Boot 查询 `0x50`、进入 `0x51`、准备 `0x52`、分包 `0x53`、完成 `0x54` 全部使用 `0xFC`
  - BMS：上述全部命令统一使用 `0x01`
- 仪表会话 OTA 放开：
  - 取消 `sessionMode === 'instrument'` 对 OTA 的禁用条件。
  - 自动 OTA 检查在仪表会话下也允许触发。
- 后端 OTA 检查兼容：
  - `device_id` 改为可选。
  - 有 `device_id` 时继续走现有绑定校验和设备配置映射。
  - 无 `device_id` 时直接按 `model` 反查 `battery_models -> device_config_id`，再匹配 OTA 包。

## 2. 关键流程
1. 设备详情页进入仪表临时会话。
2. OTA 检查按 `model + version` 请求 `/api/v1/app/battery/ota/check`。
3. 后端根据模型找到 `device_config_id`，返回是否需要升级及固件下载地址。
4. 前端点击升级后，按设备类型选择固定 Boot 目标地址：
   - 仪表 `0xFC`
   - BMS `0x01`
5. `bootOtaUpgrade()` 全流程按该地址下发 Boot 命令。

## 3. 测试策略
- `cd fjbms-uniapp && pnpm exec tsc --noEmit`
- `cd backend && go test ./internal/service/...`
- 手工验证：
  - BMS 详情页 OTA 查询和升级
  - 仪表临时会话 OTA 查询和升级
  - 查询请求日志中目标地址是否按设备类型固定

## 4. 兼容性与迁移
- 不涉及数据库迁移。
- 既有基于 `device_id` 的 BMS OTA 检查链路保持兼容。
