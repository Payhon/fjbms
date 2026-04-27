# FEAT-0048 BMS 4G 通讯调试管理 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-27
- related_feature: FEAT-0048
- version: v0.1.0

## 1. 静态检查与命令
- [x] `cd backend && go test ./internal/bmsbridge/... ./internal/service/... ./internal/api/...`
- [x] `cd backend && go test ./internal/uplink ./internal/service ./internal/bmsbridge/...`
- [ ] `cd frontend && pnpm build`

## 2. 手工回归场景
- [ ] `BMS管理 > 通讯调试管理` 菜单可见、可进入
- [ ] 按设备 ID 查询单个 4G BMS 设备日志
- [ ] 切换事件类型过滤仅显示目标日志
- [ ] 实时开关开启后，列表可收到新增日志
- [ ] 点击详情可查看原始 payload 与解析摘要
- [ ] 非 4G BMS 设备不会写入日志表

## 3. 已完成结果
- 后端定向 `go test` 已通过。
- 已在生产环境验证目标 4G 设备存在持续 MQTT 上行，bridge 修复后可生成 `uplink_raw/uplink_decoded/uplink_parsed/downlink_publish` 日志，且主平台 `device_batteries.soc/soh/updated_at` 可随报文刷新。
- 已补充“无 `device_config` 时按业务数据自动上线并刷新默认心跳 TTL”的后端兜底实现，待生产部署后继续核验首页/详情在线态。
- 前端运行态和整包构建尚未完成。
