# FEAT-0007 蓝牙 BMS 经 App 上云 + 后台 BMS 实时/历史可视化 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-03-10
- related_feature: FEAT-0007
- version: v0.2.1

## 日志
1. 后端新增 APP 上报 DTO 与 API：
   - `backend/internal/model/app_battery.http.go`
   - `backend/internal/api/app_battery.go`
   - `backend/router/apps/app_battery.go`
2. 后端实现上报服务链路：
   - `backend/internal/service/app_battery.go`
   - 完成白名单校验、64KB 快照限制、事务写历史/当前、`device_batteries` 同步、WS 事件发布。
3. 后端配置新增灰度开关：
   - `backend/configs/conf.yml`
   - `backend/configs/conf-dev.yml`
   - `backend/configs/conf-test.yml`
4. UniApp 接入云上报与跨端传输选择：
   - `fjbms-uniapp/service/app-battery.ts` 增加 `appBatteryReport`
   - `fjbms-uniapp/pages/device-battery/useBatteryDetail.ts` 增加上报队列与微信 WS 桥接选择逻辑。
5. Web BMS 面板改造为云端优先：
   - `frontend/src/views/device/details/modules/bms-panel/index.vue`
   - 增加云端实时订阅、核心曲线、快照时间线；保留参数直连读写。
6. 前端查询兼容性补充：
   - `frontend/src/service/api/device.ts`
   - `telemetryDataCurrentKeys` 支持 `keys` 数组按重复 query 参数编码，适配后端 `[]string` 绑定。
7. 后端补充单元测试：
   - `backend/internal/service/app_battery_report_test.go`
   - 覆盖核心 key 白名单、非法类型与快照 64KB 限制。
8. 后端新增 BLE Relay 指令链路：
   - `backend/internal/api/app_battery_relay.go`
   - `backend/internal/service/app_battery.go`
   - `backend/internal/model/app_battery.http.go`
   - `backend/router/apps/battery.go`
   - `backend/router/router_init.go`
   - 支持 App Relay WS 会话注册/心跳、owner 选举、WEB 指令下发与结果查询。
9. UniApp 新增 Relay WS 客户端：
   - `fjbms-uniapp/pages/device-battery/useBatteryDetail.ts`
   - BLE 连接成功后自动连 Relay WS，实时接收 WEB 指令并执行 `readParam/writeParam/writeRegisters` 回执。
10. Web 参数面板接入 BLE Relay：
   - `frontend/src/views/device/details/modules/bms-panel/index.vue`
   - `frontend/src/service/api/bms.ts`
   - BLE-only 设备参数设置不再依赖 MQTT，改走 APP 蓝牙中继通道。
11. 后端新增 APP 连接状态同步接口与在线态联动：
   - `backend/internal/model/app_battery.http.go`
   - `backend/internal/api/app_battery.go`
   - `backend/router/apps/app_battery.go`
   - `backend/internal/service/app_battery.go`
   - 新增 `POST /api/v1/app/battery/connection-status`，支持蓝牙连接/断开主动同步 `devices.is_online`。
12. 后端在线态口径联动增强：
   - `backend/internal/service/app_battery.go`
   - `POST /api/v1/app/battery/report` 成功后（BLE-only）同步设备在线状态；
   - Relay 会话断开时在“无 owner”条件下主动置离线，并发布 `device:{id}:status`。
13. 配置项补充：
   - `backend/configs/conf.yml`
   - `backend/configs/conf-dev.yml`
   - `backend/configs/conf-test.yml`
   - 新增 `sync_device_online`、`offline_on_ble_disconnect`、`online_ttl_sec`。
14. UniApp 主动连接态上报：
   - `fjbms-uniapp/service/app-battery.ts`
   - `fjbms-uniapp/pages/device-battery/useBatteryDetail.ts`
   - BLE 连接成功/断开时主动调用连接态同步接口。
15. 修复后台 BMS 面板 PACK 电压取值口径：
   - `frontend/src/views/device/details/modules/bms-panel/index.vue`
   - `fjbms-uniapp/pages/device-battery/useBatteryDetail.ts`
   - `backend/internal/service/app_battery.go`
   - `backend/configs/bms-bridge-rules.yml`
   - 后台 PACK 电压改为读取 `packCellSumVoltageV`（与小程序电芯页顶部总电压一致），不再使用在部分设备上会返回 `6553.5V` 哨兵值的 `vPackV` 作为总压展示/历史曲线口径。
16. 调整后台设备详情页在 BMS 电池详情模式下的 TAB 收口：
   - `frontend/src/views/device/details/index.vue`
   - 当通过电池管理入口进入详情（`bms=1`）时，仅保留 `BMS面板` 与 `连接` 两个 TAB，其余通用设备 TAB 隐藏，减少无关信息干扰。
