# FEAT-0007 蓝牙 BMS 经 App 上云 + 后台 BMS 实时/历史可视化 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-03-02
- related_feature: FEAT-0007
- version: v0.1.0

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
