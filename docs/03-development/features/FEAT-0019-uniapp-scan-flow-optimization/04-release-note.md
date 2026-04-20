# FEAT-0019 UniApp 扫码流程优化 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-04-18
- related_feature: FEAT-0019
- version: v0.1.0

## 1. 发布内容
- UniApp 扫码入口按设备类型统一分流：
  - 若扫码结果已命中“我的设备”列表中的 `ble_mac` 或 `item_uuid`，则直接进入设备详情页；
  - BMS (`0xAC`) MAC 继续走 BLE 搜索与绑定向导；
  - 仪表 (`0xAA`) MAC 直接进入设备详情页临时 BLE 会话模式；
  - UUID 扫码兼容路径保留。
- UniApp 蓝牙扫描页点击设备卡片时，若广播 MAC 判定为仪表 (`0xAA`) 设备，则直接进入临时 BLE 会话详情模式，并带上 `device_name` 作为会话展示名。
- UniApp BMS 绑定成功后，现会优先复用绑定向导阶段已经建立的 BLE 会话，并把设备详情的云端详情请求改为后台刷新，减少“添加成功后再等一次重连和首包”的等待时间。
- UniApp 已绑定设备在“我的设备列表”保持蓝牙连接时，扫码直达详情页现会优先复用当前缓存中的 BLE 会话，不再默认重新建连，重点缩短 iOS 上的进入详情等待时间。
- UniApp 现已为 iOS 设备增加 BLE `deviceId` 本地记忆与优先直连策略；再次进入设备详情时会先尝试直连，失败后才回退到短扫，避免默认先扫满 5 秒。
- UniApp 蓝牙扫描页补充蓝牙 API 超时保护，修复 iOS App 端首次进入页面时偶发“顶部已停止扫描、按钮持续 loading、无发现日志”的假死问题。
- UniApp 添加向导页补充 BLE 停扫 best-effort 保护，修复 iOS App 端从蓝牙扫描页进入后第一步“连接蓝牙设备”偶发长期停留在“待执行”的问题。
- UniApp BLE transport 补充 iOS 服务树发现容错重试，修复连接已建立但随后报 `getBLEDeviceCharacteristics:fail no characteristic` 的连接失败问题。
- UniApp BLE transport 现会按写特征真实属性为 iOS 优先选择 `write with response`，修复连接完成后 `readUuid()` 首包长时间无响应、第二步持续执行中的问题。
- UniApp BLE transport 现已在 iOS App 端连接成功后增加约 `820ms` 的首包 warm-up，修复设备在连接完成后立即发送 `readUuid()` 首包时无响应、第二步长期卡住的问题。
- UniApp BLE transport 现已为请求期内的 `writeBLECharacteristicValue` / `readBLECharacteristicValue` 增加 soft-timeout 保护，修复 App iOS 原生桥接层 BLE API 无回调时第二步无声卡死的问题。
- UniApp BLE transport 现已针对 iOS 写入回调启用自适应快速放行，并将正常 notify 场景下的 timeout 日志收敛为单次 `callback latency diagnostic`，优化首页进入设备详情后的首包时延与控制台可读性。
- 设备类型前缀统一收敛到 `fjbms-uniapp/common/device-provision/device-prefix.js`，TS/JS 入口共享单一静态配置文件。
- BMS 绑定成功后不再停留首页，改为直接进入 `/pages/device-battery/detail?device_id=...`。
- UniApp 蓝牙扫描页“正在匹配：{mac}”提示现已修复为正确显示实际 MAC。
- 仪表详情页新增“继续扫码绑定 BMS”能力，调用既有 `configureMeterMac({ meterAddress: 0xFC, mac })` 写入新目标。
- 仪表临时会话下隐藏 OTA 入口，避免在无 `device_id` 场景触发云端 OTA 检查。

## 2. 影响范围
- `fjbms-uniapp/`：扫码入口、设备绑定向导、设备详情页临时 BLE 会话
- `docs/`：功能文档与项目看板

## 3. 升级步骤
- 发布 UniApp 前端包即可，无需新增后端接口或数据库迁移。
- 本次新增的 handoff 与 BLE 会话复用均为客户端内存/本地存储级逻辑，无额外服务端升级步骤。
- 若调整设备类型前缀，仅需修改 `device-prefix.js` 中的静态配置并重新构建客户端。

## 4. 回滚步骤
- 如需回滚，恢复以下改动即可：
  - 扫码入口分流逻辑；
  - 设备详情临时仪表会话模式；
  - 绑定成功后的自动跳转；
  - `device-prefix.js` 静态前缀配置。
- 本功能未引入数据库或接口协议变更，前端代码回滚即可恢复旧行为。

## 5. 已知问题
- 尚未完成本轮真机蓝牙联调闭环，需重点验证 iOS App 端蓝牙扫描启动稳定性、从扫描页进入添加向导的连接启动与服务树发现稳定性、连接成功后 `post-connect warmup` 是否足以覆盖设备首包准备时间、已连接设备扫码直达详情时是否稳定接管现有 BLE 会话、remembered `deviceId` 是否能稳定用于 iPhone 详情页直连、直连失败后的短扫回退是否及时命中、首页进详情与后续轮询的首包时延是否已收敛、请求期内 BLE 写入/探测 API 是否仍会出现无回调、BLE 扫描点击仪表设备后的临时会话首连体验，以及二次扫码写目标地址时序。
