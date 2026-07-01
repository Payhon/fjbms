# FEAT-0041 UniApp OTA 地址口径统一与仪表会话升级支持 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-06-30
- related_feature: FEAT-0041
- version: v0.3.0

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
- 仪表扫码提示显隐：
  - 仪表临时会话下，`readAllStatus()` 成功后 `status.value` 存在，视为已能读取下方 BMS 状态。
  - `useBatteryDetail` 将现有 `instrumentPassthroughUnavailable` 返回给详情页；该状态在仪表会话连续 3 次读 BMS 状态超时或无响应后置为 true。
  - “仪表临时连接”浮动提示仅在仪表会话允许扫码交接、当前蓝牙已连接、未连接中、未读取到 BMS 状态，且不处于首帧读取等待中或已确认无 BMS 状态时展示。
  - 若有线仪表首帧读取成功，浮动提示和收起后的仪表入口均不展示；若有线仪表未接 BMS 或蓝牙透传型仪表未绑定 BMS，连续 3 次失败后隐藏 loading、回到主面板并展示扫码提示。
  - 人工重新读取、重新连接和进入新仪表会话时清除 `instrumentPassthroughUnavailable`，重新进入读取流程。
- 补充：
  - FEAT-0046 已将“仪表升级包管理 + UniApp 手动选包升级”从本功能中拆出，当前文档主要描述地址口径与仪表会话 OTA 能力基础。

## 2. 关键流程
1. 设备详情页进入仪表临时会话。
2. OTA 检查按 `model + version` 请求 `/api/v1/app/battery/ota/check`。
3. 后端根据模型找到 `device_config_id`，返回是否需要升级及固件下载地址。
4. 前端点击升级后，按设备类型选择固定 Boot 目标地址：
   - 仪表 `0xFC`
   - BMS `0x01`
5. `bootOtaUpgrade()` 全流程按该地址下发 Boot 命令。
6. 详情页仪表会话进入后先发起 BMS 状态读取：
   - 读取中不展示扫码提示，避免有线仪表首屏误引导。
   - 读取成功后展示正常仪表盘数据，不展示扫码提示。
   - 连续 3 次读取失败并确认无透传或无下方 BMS 后，关闭 loading，展示主面板和继续扫码绑定 BMS 的提示。

## 3. 测试策略
- `cd fjbms-uniapp && pnpm exec tsc --noEmit`
- `cd fjbms-uniapp && git diff --check -- pages/device-battery/detail.vue pages/device-battery/useBatteryDetail.ts lang/zh-CN.ts lang/en-US.ts`
- `cd backend && go test ./internal/service/...`
- 手工验证：
  - BMS 详情页 OTA 查询和升级
  - 仪表临时会话 OTA 查询和升级
  - 查询请求日志中目标地址是否按设备类型固定
  - 有线仪表未接 BMS 时 3 次失败后返回主面板并显示扫码提示

## 4. 兼容性与迁移
- 不涉及数据库迁移。
- 既有基于 `device_id` 的 BMS OTA 检查链路保持兼容。
