# FEAT-0019 UniApp 扫码流程优化 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-04-18
- related_feature: FEAT-0019
- version: v0.1.0

## 1. 测试范围
- 设备类型前缀静态配置化
- 扫码入口统一分流
- BLE 扫描列表点击分流
- 已添加设备扫码直达详情
- BMS 绑定成功后跳转详情页
- 仪表临时 BLE 会话详情与二次扫码绑定 BMS

## 2. 测试环境
- 当前 Codex 桌面执行环境
- Node/TypeScript 静态校验：`cd fjbms-uniapp && pnpm exec tsc --noEmit`
- 代码搜索回归：`rg -n "0xaa|0xAA|0xac|0xAC|'AA'|'AC'|\"AA\"|\"AC\"" fjbms-uniapp`
- 待补充：UniApp 真机或开发者工具联调结果

## 3. 用例结果
- 通过：默认前缀配置下，扫码解析已能将 `ACxxxx...` 识别为 `bms`、`AAxxxx...` 识别为 `meter`。
- 通过：`useAddDeviceActionSheet.ts` 与 `custom-tab-bar/index.js` 均改为依赖统一解析结果，入口分流口径一致。
- 通过：BMS 绑定向导和 UUID 绑定页已在成功后读取 `device_id` 并跳转设备详情页。
- 通过：摄像头扫码入口已新增“先匹配我的设备列表”的分支，命中 `ble_mac` 或 `item_uuid` 后将直接进入 `/pages/device-battery/detail?device_id=...`。
- 通过：仪表扫码已改为直接进入临时 BLE 会话详情模式，详情页支持继续扫码并写入新的 BMS 目标。
- 通过：蓝牙扫描页已在设备行中持久化 `deviceType`，点击 `AA` 前缀且广播 MAC 可用的仪表卡片时将直接进入 `/pages/device-battery/detail?session_mode=instrument&ble_mac=...&allow_scan_handoff=1&device_name=...`。
- 通过：蓝牙扫描页点击 `AC` 前缀 BMS 设备或广播缺少 `advMac` 的设备时，仍按原逻辑进入 `provision-wizard`，未把不确定设备误导向仪表临时会话。
- 通过：蓝牙扫描页现已为 `openBluetoothAdapter` / `startBluetoothDevicesDiscovery` / `stopBluetoothDevicesDiscovery` 增加超时保护，避免 iOS App 端蓝牙 API 回调不返回时按钮持续 loading、扫描不启动。
- 通过：`provision-wizard.vue` 在开始连接前改为使用带超时的 best-effort 扫描停止逻辑，避免 iOS App 端 `stopBluetoothDevicesDiscovery` 不返回时，步骤一长期停留在“待执行”。
- 通过：`uni-ble-transport.ts` 已将连接前 / discover 结束后的 `stopBluetoothDevicesDiscovery` 与 `closeBluetoothAdapter` 改为 best-effort，降低 iOS App 端 BLE stop/close 回调挂起对连接链路的影响。
- 通过：`uni-ble-transport.ts` 现已将 `getBLEDeviceServices / getBLEDeviceCharacteristics` 改为“空结果或 fail 都重试”，并对 iOS 提高重试窗口，避免 `getBLEDeviceCharacteristics:fail no characteristic` 在服务树尚未就绪时直接中断连接流程。
- 通过：`uni-ble-transport.ts` 已在 iOS 端根据写特征真实 `properties` 优先选择 `write with response`，降低 `readUuid()` 首包在 App iOS 端表面写入成功但设备未响应的风险。
- 通过：`uni-ble-transport.ts` 已在 iOS App 端连接完成后增加约 `820ms` 的 `post-connect warmup`，避免设备尚未准备好时立即发送 `readUuid()` 首包导致第二步长期执行中。
- 通过：`uni-ble-transport.ts` 已为请求期内的 `writeBLECharacteristicValue` / `readBLECharacteristicValue` 增加 soft-timeout 保护，避免 App iOS 原生桥接层无回调时第二步无声卡死。
- 通过：`uni-ble-transport.ts` 已将 iOS 写入 soft-timeout 改为自适应快速放行，并对重复 timeout 告警节流，降低首页进详情首连与后续轮询的额外等待时间。
- 通过：`provision-wizard.vue` 绑定成功后会先把当前 BLE 会话接管到 `ble-client-cache.ts`，再写入 `detail-handoff` 并跳转详情页，不再无条件销毁现有 BLE 连接。
- 通过：`useBatteryDetail.ts` 命中 handoff 时会优先接管已接入缓存的 BLE 会话，并将 `appBatteryDetail` 改为后台刷新，避免再次串行等待“云端详情 -> BLE 重连 -> 首包读取”。
- 通过：`useBatteryDetail.ts` 在普通 `loadById(device_id)` 成功拉取详情后，也会优先尝试复用 `ble-client-cache.ts` 中相同 `ble_mac` 的活跃会话；因此“我的设备列表已连接 -> 扫码直达详情”不再必然重连。
- 通过：`ble-client-cache.ts` 已为 iOS 新增 `deviceId` 持久化直连候选和两段式扫描回退；理论上已可避免“进入详情后固定先等待 5 秒扫描”的连接模式。
- 通过：`ble-scan.vue` 的“正在匹配”提示已改为本地格式化插值，`mode=qr&mac=...` 不再显示字面量 `{mac}`。
- 通过：`params-tab.vue` 已在仪表临时会话下隐藏 OTA 入口，且 OTA 设备类型判定改为统一 helper。
- 通过：仓库搜索确认 `fjbms-uniapp/` 内不存在散落在业务逻辑里的 `AA/AC` 设备类型硬编码，检索结果仅剩 `device-prefix.js` 配置源文件本身。
- 通过：删除 `device-prefix.ts` 后，TS 页面仍可通过 `device-prefix.js` 的 JSDoc 标注完成类型检查，未出现导入或类型退化问题。
- 通过：`pnpm exec tsc --noEmit` 校验通过，无新增 TypeScript 类型错误。
- 通过：`uni-ble-transport.ts` 现已将 iOS 正常 notify 驱动下的 `writeBLECharacteristicValue` 软超时日志收敛为单次 info 诊断，不再在轮询期间持续刷屏。
- 通过：`uni-ble-transport.ts` 现已将该类一次性写入日志显式标注为 `callback latency diagnostic`，与真正的 `BLE request timeout` 区分。

## 4. 缺陷与风险
- 尚未完成真机蓝牙联调，以下场景仍需设备侧验证：
  - 已添加设备通过扫码直达详情页后的首连时延与页面体验；
  - iPhone 上“我的设备列表已连接 -> 扫码直达详情”是否稳定直接接管已有 BLE 会话，而不是再次重连；
  - iPhone 冷启动后首次进入某已绑定设备详情时，若本地已有 remembered `deviceId`，是否会优先出现 `ios direct connect try` 并明显缩短等待；
  - iPhone 若 remembered `deviceId` 失效，是否会先走短扫回退，而不是再次固定等待满 `5s`；
  - BMS 绑定成功后跳转详情页时，是否稳定复用原 BLE 会话，且不再出现第二次 discover/connect；
  - BMS 绑定成功后即使 `appBatteryDetail` 响应偏慢，详情页是否仍能先展示基础信息并快速拿到首包状态；
  - BLE 扫描列表点击 `AA` 前缀仪表卡片后的路由分流与首连体验；
  - iOS App 端首次进入蓝牙扫描页时，`stopBluetoothDevicesDiscovery` 超时放行后是否可稳定收到 `discovery started` 与设备发现回调；
  - iOS App 端从蓝牙扫描页进入 `provision-wizard` 后，步骤一是否稳定进入 `doing` 并打印 `connect start`；
  - iOS App 端从蓝牙扫描页进入 `provision-wizard` 后，`createBLEConnection` 成功时是否还能稳定拿到 `ffc0 / ff03 / ffc1` 服务与特征，不再报 `getBLEDeviceCharacteristics:fail no characteristic`；
  - iOS App 端在打印 `[ble] post-connect warmup` 后执行 `readUuid()` 时，是否可稳定收到首个回复帧并进入第三步，不再长期停留在“读取设备唯一编号（执行中）”；
  - iOS App 端若首包仍失败，是否能够继续看到一次性的写入 soft-timeout 诊断、fallback 告警或标准 `BLE request timeout`，而不是完全无日志卡死；
  - iOS App 端首页进入设备详情页时，首个 `status obj` 打印耗时是否明显收敛，且重复 timeout 日志是否已基本消失；
  - 仪表临时 BLE 会话下的自动连接成功率；
  - 仪表详情页二次扫码后 `configureMeterMac` 的协议写入和设备刷新时序；
  - APP 与微信小程序扫码 API 在不同机型上的体验一致性。

## 5. 结论
- 当前代码实现与静态校验已完成，建议进入真机联调/验收阶段。
