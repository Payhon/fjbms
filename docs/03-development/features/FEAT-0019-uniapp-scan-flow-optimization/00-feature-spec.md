# FEAT-0019 UniApp 扫码流程优化 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-03-22
- related_feature: FEAT-0019
- version: v0.1.0

## 1. 背景与目标
- 背景：
  - 当前 UniApp 扫码入口仅区分 `MAC/UUID` 两类结果，未按设备类型拆分 `BMS` 与仪表流程。
  - 设备类型前缀规则当前分散在协议文档和个别逻辑中，缺少统一静态配置，后续若前缀变化，维护成本高且容易遗漏。
  - 当前 BMS 扫码绑定成功后停留在“添加成功/返回首页”，与原始流程文档“自动连接并跳转仪表盘”的目标不一致。
- 目标：
  1. 按 `doc/oriigin/移动端扫码流程.md` 的规则，将扫码得到的 MAC 分流为 `BMS` 与仪表两条主链路。
  2. 将设备类型前缀抽离为静态配置，业务代码不得硬编码 `AA/AC`。
  3. BMS 绑定成功后直接进入设备详情页；仪表扫码进入本地 BLE 临时会话详情页。
  4. 保留现有 UUID 扫码兼容路径，不影响遗留设备自动补建流程。

## 2. 范围
### In Scope
- 新增 UniApp 静态设备前缀配置模块，统一收敛到单一 `device-prefix.js` 文件，供 TS/JS 共用。
- 调整 UniApp 扫码入口解析与页面跳转逻辑：
  - `common/composables/useAddDeviceActionSheet.ts`
  - `custom-tab-bar/index.js`
  - `common/device-provision/scan-code.ts`
- BMS 扫码流程保持现有蓝牙匹配与绑定向导，但绑定成功后直接跳转设备详情页。
- 仪表扫码新增“本地 BLE 临时会话”详情模式，并在该模式提供“继续扫码绑定 BMS”入口。
- 更新功能文档、实现日志、测试报告、发布说明和项目看板。

### Out of Scope
- 不修改 `doc/oriigin/*` 历史原始文档。
- 不新增后端扫码分流接口或前缀下发接口。
- 不把 `0xFC` 仪表目标地址、OTA 目标地址等协议常量纳入本次前缀配置化范围。
- 不新增独立的仪表专用详情页 UI，首版复用现有设备详情页。

## 3. 验收标准
1. 扫描 `MAC` 时，前缀命中静态配置后可稳定分流：
   - `BMS` 前缀进入 BMS 绑定流程；
   - 仪表前缀进入仪表临时详情流程；
   - 未命中前缀的 MAC 不按 BMS 或仪表误处理。
2. 设备类型前缀仅存在于统一静态配置文件中，业务逻辑不再直接出现 `AA/AC` 设备类型判断。
3. `useAddDeviceActionSheet.ts` 与 `custom-tab-bar/index.js` 对同一二维码返回一致的分流结果。
4. BMS 扫码绑定成功后直接进入设备详情页，而不是停留首页。
5. UUID 扫码兼容路径仍可正常绑定设备并进入设备详情页。
6. 仪表扫码进入临时 BLE 会话详情页后，可继续扫码 BMS，并仅接受 `BMS` 类型 MAC 触发 `configureMeterMac`。

## 4. 风险与约束
- `custom-tab-bar/index.js` 需要与 TS 页面共享同一份常量源，静态配置文件需兼容 JS `require` 与 TS `import` 使用。
- 仪表临时会话模式没有云端 `device_id`，需要避免误触发依赖 `device_id` 的 OTA、连接态上报与 MQTT/Relay 逻辑。
- 设备前缀后续若扩展，必须仅修改静态配置文件，不得重新在业务逻辑中散落判断。

## 5. 回滚方案
- 回滚 `FEAT-0019` 对应 UniApp 提交，恢复当前扫码入口和绑定成功后返回首页的行为。
- 若临时会话模式出现问题，可先保留前缀配置化与扫码入口分流，暂时下线仪表临时详情入口。
