# FEAT-0046 仪表 OTA 升级包与 UniApp 独立升级链路 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-28
- related_feature: FEAT-0046
- version: v0.1.0

1. 梳理现有 `ota_upgrade_packages`、后台升级包页、UniApp 参数页与 APP OTA 检查链路，确认 BMS OTA 与仪表 OTA 需要拆成两条合同。
2. 新增 `backend/sql/51.sql`，为 `ota_upgrade_packages` 增加 `device_kind` 字段并回填历史数据为 BMS。
3. 后端 `Create/Update/GetOTAUpgradePackageListByPage` 补充 `device_kind` 处理：
   - 默认 BMS；
   - 仪表包只校验名称与固件地址；
   - 仪表包在服务层写入兼容字段占位。
4. `CheckBatteryOtaForApp` 限定只匹配 `device_kind=1` 的 BMS 升级包，避免仪表包污染现有检测逻辑。
5. 新增 `GetMeterOtaPackagesForApp()` 与 `/api/v1/app/battery/ota/meter-packages`。
6. 后台升级包管理页改为双 TAB，仪表 TAB 使用精简字段；任务页与批量 OTA 包拉取显式固定 `device_kind=1`。
7. UniApp 参数页新增“仪表升级”卡片与仪表固件列表弹层；蓝牙仪表详情页隐藏旧 OTA Cell 与红点。
8. 仪表升级改为“手动选包后下载”，并复用现有 Boot OTA 进度条，但目标地址固定 `0xFC`。
9. 新增 `backend/internal/service/ota_device_kind_test.go` 作为最小单测覆盖。
10. 新增 FEAT-0046 文档并同步看板。
11. 根据安卓真机反馈继续排查仪表包列表为空问题，确认根因是 `/api/v1/app/battery/ota/meter-packages` 仅按 JWT `claims.TenantID` 过滤，未与 APP 侧 `X-TenantID` 租户头对齐。
12. 修复 `GetMeterOtaPackagesForApp()`：改为 API 层显式透传 `X-TenantID`，服务层按“header -> claims -> 默认租户”解析租户，并兼容返回公共仪表包；同时补充查询日志用于生产排障。
13. 根据后续真机日志继续收敛，确认已登录 `app/battery` 接口不应信任客户端缓存租户头；调整为“claims -> header -> 默认租户”，并在 header/claims 不一致时记录告警日志。
14. 根据 OTA 真机日志继续排查升级失败问题，确认仪表 OTA 发往 `0xFC` 时设备回包源地址仍为 `0x01`，导致 transport 误判超时；已在 BLE、MQTT socket、MQTT WS 三套 Boot 应答匹配逻辑中兼容该地址特例。
15. 依据 `_resources/仪表升级日志.txt` 对齐仪表 OTA 真实链路，并结合蓝牙升级约束修正参数：`0x50` 广播查询、跳过 `0x51`、蓝牙链路下 `0x52` 固定携带 `9600` 参数；这些差异仅作用于仪表升级分支，不影响 BMS OTA 默认流程。
16. 优化仪表详情状态轮询：针对“蓝牙已连通但尚未建立 BMS 透传”的正常场景，在仪表会话下连续状态读取超时达到阈值后停止轮询，不再反复重试；同时保留蓝牙连接与 `client` 以支持仪表升级。
17. 修复 Android 仪表详情连接串设备问题：扫描页跳转时透传真实 BLE `deviceId`，详情页仪表会话优先使用该候选；BLE 连接缓存会过滤与目标 AA MAC 不兼容的 MAC 型候选，避免被历史 AC 设备连接任务干扰。
18. 修复 iOS 仪表 OTA 末段 0x53 超时后重试立即失败问题：BLE transport 在请求超时后若发现超过超时阈值的陈旧 pending，会清理残留状态后再执行重试，避免卡在 95% 左右无法继续写包。
19. 修正 Boot `0x53` 回包 `status=5` 的语义与文案：该状态按“固件包大小与设备不一致”处理，不再显示为“硬件型号不匹配”。
20. 根据 Android 复测日志继续加固连接阶段：同一 MAC 的 `inFlight` 连接任务、BLE 连接串行队列等待上一任务超过 8s 时不再无限阻塞；`createBLEConnection` 增加硬超时，Android 6.5s、iOS 9s，避免系统 API 不回调导致详情页长期停留在“连接中”。
21. 根据 `_resources/ble-metric-upgrade-console-android.txt` 排查 Android 仪表 OTA 17% 失败：日志显示写包稳定 ACK 到 `packetIndex=127/requested=128`，第 128 包位于 8KB 边界后 12s 无回包。仪表 OTA 的 `0x53` 超时调整为 45s；Android 仪表升级时使用带响应写、最小帧间隔 180ms、ACK 后额外等待 40ms，以适配 Bootloader 页/扇区擦写耗时与 Android BLE 写入节奏。
22. 根据 `_resources/ble-metric-upgrade-console-android-02.txt` 继续排查 Android 仪表 OTA 13% 失败：日志显示 `0x53` ACK 到 `packetIndex=63/requested=64` 后，第 64 包位于 4KB 边界，等待 45s 无回包且重试时 Android BLE 写入报错。仅在 Android 仪表 OTA 分支加大帧间隔到 220ms、包间延迟到 100ms，并在每个 4KB 固件边界写入前等待 1500ms；这些参数只作用于仪表升级，不影响 BMS OTA 与普通通讯。
23. 根据 `_resources/ble-metric-upgrade-console-android-03.txt` 回归确认，20 字节 BLE 分片会导致首个 `0x53 packetIndex=0` 无 ACK。该仪表蓝牙透传模块按单次 BLE 写入透传 Boot 帧，不能把一个 Boot 帧拆成多次 BLE 写入；因此撤回 Android 仪表 OTA 的 20 字节分片，继续保持单帧写入。
24. 根据 `_resources/ble-metric-upgrade-console-android-04.txt` 判断 Android 仪表 OTA 实际已完成：最后一个 `0x53 packetIndex=1613` 回 `requested=1614`，等于总包数；随后 `0x54` finalize 首次等待应答超时，第二次发送时设备已断开/重启。将 Android 仪表 OTA finalize 优化为：全部数据包 ACK 后，`0x54` 超时或断开按成功收敛，并静默该预期超时日志，避免控制台误导性告警。
25. 优化蓝牙扫描页停止与超时状态：停止扫描时立即递增扫描会话、清理扫描超时定时器、移除设备发现监听并复位 `isScanning`；设备发现回调入口校验当前扫描状态，避免停止后继续打印发现设备；新增 30s 扫描时长超时，超时后自动停止扫描并恢复按钮状态。
26. 根据 `_resources/ble-metric-upgrade-console-ios.txt` 排查 iOS 仪表 OTA 95% 失败：日志显示最后一个 `0x53 packetIndex=1613` 已回 `requested=1614`，全部数据包已写完；随后 `0x54` finalize 后设备断开并返回 `writeBLECharacteristicValue:fail no device`。将 iOS 仪表 OTA 纳入全部 ACK 后 finalize 超时/断开成功收敛，并识别 `no device`、`not connected` 等断连文案；同时仪表 finalize 静默请求不再触发 iOS 替代写模式重试，避免设备重启后的误导性失败日志。
27. 根据 `_resources/ble-metric-upgrade-console-ios-02.txt` 复核 iOS 升级完成日志：最后一个 `0x53 packetIndex=1613` 回 `requested=1614`，随后发送 `0x54` 并按预期 finalize timeout 收敛，确认界面完成对应真实写包完成。同步优化 iOS 扫描进入详情连接耗时：扫描页传入的 UUID 型 `deviceId` 不再被 MAC 兼容过滤误判，允许直接连接；详情页主动取消旧连接后，连接锁等待缩短到 1.2s，避免被旧 AC 设备连接任务拖慢约 8s。
28. 针对线上用户“还没开始写固件前失败”问题，新增开发者模式下端上仪表 OTA 调试日志：本地缓冲最近 120 条关键日志，覆盖选包、升级包列表、固件下载、Boot `0x50/0x52` 前置、首包预览、关键 ACK、失败错误对象与成功收敛证据；在仪表升级卡片下方展示并支持复制/清空，不新增后端接口，不影响 BMS OTA。
29. 针对微信小程序主包 2053KB 超过 2048KB 限制，优化包体：将仪表 OTA 调试日志模块从 `common/` 移入 `pages/device-battery` 分包，避免进入主包；删除未被源码引用但会被打入主包的 `static/js/moment.js`，释放约 85KB 静态资源空间。
30. 根据 `_resources/ble-metric-upgrade-log-mp.txt` 排查微信小程序仪表 OTA 95% 失败：日志显示数据包 ACK 已到 `packetIndex=1599/requested=1600`，最后一个 `0x53 packetIndex=1613` 写入时小程序 BLE 栈返回 `10006/writeValueToCharacteristics`，App 侧尚未发出 `0x54`。仪表分支新增终端数据包写入错误收敛：仅当当前包为最后一个数据包且错误为 BLE 连接/特征写入终止类错误时，不再重发 `0x53`，改为进入 `0x54` finalize，并沿用全部数据写完后的超时/断开成功收敛；若数据包应答阶段已收到设备 `0x54` 完成响应，则立即停止继续写数据。BMS OTA 默认不启用该策略。
31. 统一蓝牙 OTA 末尾边界策略：抽出 Android/iOS 蓝牙运行时选项，蓝牙 BMS 与蓝牙仪表均曾启用 `0x54` finalize 超时/断开成功收敛、最后一个 `0x53` 终端写入错误进入 finalize、数据应答阶段收到 `0x54` 后立即停止继续写数据；仪表 Android 继续单独保留慢速写包与 4KB 边界等待，BMS OTA 不使用仪表专用时序。
32. 根据 `_resources/ble-metric-upgrade-log-mp-02.txt` 复核小程序仪表 OTA“界面成功但版本未变化”问题：日志只显示 `0x54` 已发送，随后 `finalize assume success after timeout`，未收到协议要求的 `0x54 status=0` 返回。仪表 OTA 改为严格协议闭环：必须完成全部 `0x53` ACK 到 `requested == packetTotal`，等待 2s 后发送 `0x54`，且 `0x54` 必须返回 `status=0` 才显示成功；否则显示“固件数据包未完整确认”或“升级完成指令未收到设备确认”。
33. 对照旧版微信小程序 `_resources/vendor.js` 的可用 OTA 状态机经验，补齐 OTA 完成阶段稳定性：全部 `0x53` ACK 后，蓝牙 BMS 与蓝牙仪表均会将 `0x54` 按 300ms/600ms/900ms 额外补发，并且都必须收到任意一次 `0x54 status=0` 才判定成功；不再把 finalize 超时或 BLE 断开收敛为成功。同时仪表 Boot 回包源地址兼容 `0x01/0xFC/0xFD`，避免不同 Bootloader 地址差异导致有效 ACK 被过滤。
34. 按旧版小程序 `0x53` ACK 驱动发包经验优化仪表 Android OTA 速度：默认取消 ACK 后固定 `packetDelayMs`，最小帧间隔从 220ms 降为 100ms，4KB 边界等待从 1500ms 降为 300ms；若发生 `0x53` 超时重试，自动启用慢速保护参数（100ms 包间等待、1500ms 边界等待），兼顾稳定性与速度。
