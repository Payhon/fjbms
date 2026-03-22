# FEAT-0019 UniApp 扫码流程优化 - 实现日志

- status: review
- owner: payhon
- last_updated: 2026-03-22
- related_feature: FEAT-0019
- version: v0.1.0

## 2026-03-21
- 完成功能规格与技术设计，明确实现边界：
  - 设备类型前缀统一收敛到静态配置文件；
  - UUID 扫码路径保留；
  - 仪表首版复用现有设备详情页，采用临时 BLE 会话模式；
  - BMS 绑定成功后直接进入详情页。
- 完成设备前缀静态配置抽离：
  - 新增 `fjbms-uniapp/common/device-provision/device-prefix.js` 作为 TS/JS 共用真源；
  - `scan-code.ts`、`useAddDeviceActionSheet.ts`、`custom-tab-bar/index.js` 全部改为依赖该模块，不再在业务逻辑内直接判断 `AA/AC`。
- 进一步收敛设备前缀模块实现：
  - 删除 `device-prefix.ts` 同名桥接文件，避免双文件维护；
  - 在 `device-prefix.js` 中补充 JSDoc 类型标注，保证 TS 页面继续获得精确类型提示；
  - `scan-code.ts` 改为通过 `DEVICE_TYPE_BMS | DEVICE_TYPE_METER` 推导设备类型联合类型。
- 完成扫码入口统一分流：
  - 支持二维码解析结果返回 `deviceType`；
  - BMS MAC 继续进入 BLE 搜索/绑定链路；
  - 仪表 MAC 直接进入设备详情页临时 BLE 会话模式；
  - 不支持的 MAC 前缀统一提示“暂不支持该设备二维码”。
- 完成设备绑定成功后的跳转优化：
  - `provision-wizard.vue` 在绑定成功后读取 `bind` 返回的 `device_id` 并 `redirectTo` 设备详情页；
  - `uuid-bind.vue` 同步改为绑定成功后直接进入设备详情页。
- 完成仪表临时 BLE 会话模式：
  - `useBatteryDetail.ts` 新增 `sessionMode = cloud | instrument`；
  - 仪表模式下使用最小本地 `battery` 视图模型建立 BLE 连接，不发起云端详情请求，不上报连接状态/快照，不接 Relay；
  - `detail.vue` 支持解析 `session_mode=instrument&ble_mac=...` 路由参数，并展示仪表临时连接提示卡片。
- 完成仪表详情二次扫码绑定 BMS：
  - `detail.vue` 新增“继续扫码绑定 BMS”按钮；
  - 仅接受 `bms` 类型二维码；
  - 调用现有 `configureMeterMac({ meterAddress: 0xFC, mac })` 写入目标 BMS MAC，并在成功后刷新本地轮询。
- 完成参数页 OTA 显隐与设备类型判断收敛：
  - `params-tab.vue` 新增 `allowOta` 控制，仪表临时会话隐藏 OTA 操作；
  - OTA 目标地址判定改为调用 `isMeterMac()`，移除原先通过 MAC 首字节硬编码判断仪表的逻辑。
