# FEAT-0019 UniApp 扫码流程优化 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-03-22
- related_feature: FEAT-0019
- version: v0.1.0

## 1. 发布内容
- UniApp 扫码入口按设备类型统一分流：
  - BMS (`0xAC`) MAC 继续走 BLE 搜索与绑定向导；
  - 仪表 (`0xAA`) MAC 直接进入设备详情页临时 BLE 会话模式；
  - UUID 扫码兼容路径保留。
- 设备类型前缀统一收敛到 `fjbms-uniapp/common/device-provision/device-prefix.js`，TS/JS 入口共享单一静态配置文件。
- BMS 绑定成功后不再停留首页，改为直接进入 `/pages/device-battery/detail?device_id=...`。
- 仪表详情页新增“继续扫码绑定 BMS”能力，调用既有 `configureMeterMac({ meterAddress: 0xFC, mac })` 写入新目标。
- 仪表临时会话下隐藏 OTA 入口，避免在无 `device_id` 场景触发云端 OTA 检查。

## 2. 影响范围
- `fjbms-uniapp/`：扫码入口、设备绑定向导、设备详情页临时 BLE 会话
- `docs/`：功能文档与项目看板

## 3. 升级步骤
- 发布 UniApp 前端包即可，无需新增后端接口或数据库迁移。
- 若调整设备类型前缀，仅需修改 `device-prefix.js` 中的静态配置并重新构建客户端。

## 4. 回滚步骤
- 如需回滚，恢复以下改动即可：
  - 扫码入口分流逻辑；
  - 设备详情临时仪表会话模式；
  - 绑定成功后的自动跳转；
  - `device-prefix.js` 静态前缀配置。
- 本功能未引入数据库或接口协议变更，前端代码回滚即可恢复旧行为。

## 5. 已知问题
- 尚未完成真机蓝牙联调，需重点验证仪表临时会话连接稳定性与二次扫码写目标地址时序。
