# FEAT-0007 蓝牙 BMS 经 App 上云 + 后台 BMS 实时/历史可视化 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-03-04
- related_feature: FEAT-0007
- version: v0.2.0

## 1. 发布内容
- 新增 APP 上报接口 `POST /api/v1/app/battery/report`。
- UniApp 新增 BLE 云上报器（双层上报 + 队列重试）。
- 微信小程序接入 WS 桥接传输，Android/iOS 保持 MQTT-WS。
- 管理端 BMS Tab 新增云端实时与历史可视化（曲线 + 快照时间线）。
- 新增 BLE Relay 实时命令链路：
  - APP WS：`GET /api/v1/app/battery/relay/ws`
  - WEB API：`GET /api/v1/battery/relay/status/:id`、`POST /api/v1/battery/relay/command`

## 2. 影响范围
- `backend/`：APP Battery API、遥测写入链路、WS 推送链路。
- `fjbms-uniapp/`：设备详情连接策略、上报策略、Relay WS 指令执行。
- `frontend/`：设备详情 BMS 面板展示逻辑与 BLE Relay 参数设置。

## 3. 发布步骤
1. 发布后端并确认配置：
   - `bms.app_report.enabled=true`
   - `bms.app_report.bluetooth_only=true`
2. 灰度发布 UniApp 版本（先 Android/iOS，再微信小程序）。
3. 发布 Web 管理端并观察 BMS 页签云端数据与历史查询。

## 4. 回滚步骤
- 后端快速回滚：`bms.app_report.enabled=false`。
- 前端与 UniApp 可保留版本，功能将自动退化为原直连展示路径。

## 5. 已知问题
- 端到端自动化测试尚未覆盖真机 BLE 场景，需人工联调补充验收。
