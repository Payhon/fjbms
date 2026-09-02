# FEAT-0041 UniApp OTA 地址口径统一与仪表会话升级支持 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-08-31
- related_feature: FEAT-0041
- version: v0.5.0

## 发布内容
- OTA Boot 查询与升级对仪表固定使用 `0xFC`，对 BMS 固定使用 `0x01`。
- 启用仪表临时会话下的 OTA 入口。
- 后端 OTA 检查支持无 `device_id` 的模型匹配。
- 仪表临时会话读取下级 BMS 的等待时间统一为 10 秒；到期后返回主面板并展示继续扫码入口。
- v0.5.0：10 秒到期仅关闭遮罩，继续低频查询；后续 BMS 接入或完整数据迟到均可自动刷新，不必切换 Tab。
- v0.5.0：修复扫码配置超时后的异常中断；有效扫码清空旧数据，连接完成后恢复查询，取消/非法码不影响原数据。配置超时提示待确认，不重复配置。

## 影响范围
- `fjbms-uniapp/pages/device-battery/detail.vue`
- `fjbms-uniapp/pages/device-battery/useBatteryDetail.ts`
- `fjbms-uniapp/pages/device-battery/instrument-passthrough-policy.ts`
- `fjbms-uniapp/pages/device-battery/components/params-tab.vue`
- `fjbms-uniapp/service/app-battery.ts`
- `backend/internal/model/app_battery.http.go`
- `backend/internal/service/app_battery.go`

## 兼容说明
- 不修改后端接口、数据库、通用 BLE 请求超时和普通 BMS/MQTT 实时读取。
- 仪表蓝牙连接保持不变，手动重新读取或重新连接会重新开始 10 秒等待。
- v0.5.0 仅修改仪表会话、提示及测试；不修改本说明列出的历史后端/OTA 实现。参数/历史页暂停、OTA 独占、首页暖连接与扫码入口退出释放规则保留。
- 无 BMS 时持续串行查询增加少量通信/耗电，超时后 3 秒轮间等待；未承诺后台持续运行。

## 发布前验收
- 微信小程序、iOS、Android 真机验证 10 秒等待、成功回包、临界/迟到回包和人工重试。
- v0.5.0 已通过模拟、TypeScript、SFC 和微信小程序本地编译，仍待 30 秒后接入及扫码切换真机验收；当前未上传/发布。

## v0.5.0 回滚
- 定向回滚本次仪表持续查询、扫码恢复、提示文案及对应测试；恢复 10 秒后停止查询会同时恢复“后接入需人工操作”的旧行为。
- 不回滚普通 BMS/MQTT、OTA 地址、首页/扫码来源断连策略等已有改动，无数据库迁移。
