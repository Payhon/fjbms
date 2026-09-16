# FEAT-0046 仪表 OTA 升级包与 UniApp 独立升级链路 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-09-12
- related_feature: FEAT-0046
- version: v0.1.9

## 2026-09-12 OTA动态ACK超时调整

- 共享Boot控制命令首发800ms、最多3次450ms超时重发；0x53保持同包重试并将无进展预算降为3次，移除220ms宽限及补偿sleep。独立版本查询不变。
- 页面逐次透传timeoutMs，删除450ms硬限制；取消BLE完成连发，0x54首次5000ms、最多3次450ms重发（按用户最后补充），仅首发前等待300ms。
- 非ACK超时立即保留原错误失败；版本查询与4G进入Boot的耗尽超时兼容保留，限定完成后断连判定不变。零宽限不调度Android读探测。
- 无后端、协议格式、依赖及连接恢复改动；保留既有未提交修改，不提交/推送。


## 2026-09-10 BLE OTA 会话交接修复

- 复核扫描/扫码仪表临时会话：并非简单复用首页缓存；缺口包含原生断连未同步、退出仅有界等待关闭，以及旧异步收尾跨越新连接。
- transport 增加断连订阅、请求取消、按对象解绑通知路由与请求连接代次检查。保留 pending 原生错误及完成证据后通知缓存/页面；连接原生回调迟到时先收尾 create 再 close。
- 缓存统一关闭任务：同设备幂等，关闭超时/失败保留屏障，成功或明确10006/无连接解除。退出等待仍为1200ms加250ms稳定期；等待扫描租约后再次检查对象身份和引用计数。
- 复用详情会话实现30秒、最多两次、每次连接前1秒等待的恢复，重新建连/发现特征/订阅并沿用平台预热；BMS正常状态读取、仪表0x50广播版本查询；退出或切换会话取消旧任务及pending。
- OTA组件只在实际调用Boot请求后登记恢复；先完成独占/屏幕/日志finally并展示原结果，再异步恢复。独立提示恢复结果和实际版本，失败复用手动重连方法；恢复不重刷、不恢复OTA期间的普通轮询。
- 原有未提交修改保留，本轮不提交、推送或部署。无后端/数据库/协议/依赖变更；未将模拟通过等同真机稳定。

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
35. 根据 `_resources/ble-metric-ota-log.md` 优化 OTA 首尾固定等待：蓝牙 OTA 开始前建立独占 Boot 会话，主动取消并清空遗留状态读取队列，升级期间拒绝新的非 Boot 请求；蓝牙 BMS 与仪表完成阶段改为单个 5s 应答窗口，在窗口内继续按 300ms/600ms/900ms 补发 `0x54`，禁用 iOS 超时后的替代写模式重试，并严格要求实际收到 `0x54 status=0`。
36. 2026-08-03 增加仪表透传 BMS OTA：参数页新增独立 BMS 升级卡片，点击后暂停轮询、读取 BMS UUID，并在读取失败时以硬件型号和软件版本降级调用现有 `ota/check`；BMS Boot 目标显式固定为 `0x01`，仪表自身继续固定 `0xFC`。
37. 扩展 `CheckBatteryOtaForApp()` 的无 `device_id` 匹配分支：UUID在当前租户补齐型号ID和批次，未登记UUID可直接命中专属包，型号名称仅解析当前租户的 `battery_bms_models`；旧 `device_id` 路径、选包得分、版本门槛和公共包语义保持不变。
38. 增加后端 UUID/型号/租户隔离测试与 UniApp 透传策略测试，断言首个查询帧为 `55 FE 01 50 00 00 0C 39 FD`；保留真实 Android、iOS、微信小程序仪表+BMS硬件验收为待办。
39. 2026-08-05 按硬件 700ms 上限统一移动端 OTA 时序：`0x52 ACK -> 0x53` 和最后一个 `0x53 ACK -> 0x54` 均固定 300ms；`0x50`～`0x53` 单次应答超时改为 450ms，`0x53` 超时重发保留 220ms；ACK 后包间与4KB边界主动等待合计限制为600ms。蓝牙非 `0x54` 请求禁用 iOS 替代写重试并将写 API 软超时限制为300ms；蓝牙和4G/MQTT的 `0x54` 统一为单个5s严格应答窗口。
40. 2026-08-06 调整 BLE OTA 完成阶段：首个 `0x54` 计入总数，随后每隔800ms补发，最多共8次，发送时刻为 `0/800/1600/2400/3200/4000/4800/5600ms`；BLE严格应答窗口调整为6400ms。收到 `status=0` 或非零状态都会立即取消剩余定时器，非零状态明确按设备拒绝失败；超时后不再启动第二轮。MQTT/4G保持单次发送和5s窗口。
41. 2026-08-28 按客户验证方案将共享的移动端非完成帧应答超时从450ms放宽为900ms，BLE与MQTT/4G的 `0x50`～`0x53` 同步生效；保留 `0x53` 超时后220ms重发缓冲、ACK后主动等待预算、BLE `0x54` 800ms×8与MQTT/4G `0x54` 单发5s策略，待微信小程序、Android、iOS及4G真机验证成功率。
42. 2026-09-02 按客户新一轮验证方案将共享的移动端非完成帧应答超时从900ms调整为600ms，BLE与MQTT/4G的 `0x50`～`0x53` 同步生效；其余重发、主动等待和 `0x54` 完成策略保持不变，待真机继续验证。
43. 2026-09-02 完成 Android BLE OTA 传输闭环修复：全部移动端 `0x50`～`0x53` 应答超时恢复为450ms，配合220ms重发等待形成670ms节拍；Android 微信小程序与 App 在任何 Boot 命令前请求512 MTU并按实际容量限制数据包，MTU不足时明确阻断；独占会话禁止拆分 `0x53`，仅在特征明确支持时使用带响应写；进度改为有效ACK后更新，OTA期间保持屏幕常亮，并补齐MTU、帧长、ACK RTT、RSSI与重试日志。

## 2026-09-03 参照旧版 ACK 状态机修复

- 客户复测 BLE 与4G均有 `0x53` 失败，确认 MTU 不是共同根因；对照 `_resources/vendor.js` 的连续接收、期望序号推进与整帧写入，定位到450ms后销毁 pending、220ms盲等丢ACK，以及旧成功ACK错误回退和BLE原生写回调阻塞。
- BLE与MQTT共享 `0x53` 连续ACK窗口：450ms后保留同一请求220ms，有效ACK立即推进；直到670ms仍无ACK才重发，核心不再重复等待220ms。Boot解析器连续接收，混入普通帧、坏帧、旧ACK后仍能提取当前有效ACK。
- 成功ACK只接受当前期望序号；显式重发/重新准备按协议有界恢复，仅新确认进度重置恢复预算。保留全部数据ACK及真实 `0x54 status=0` 的严格成功门槛，不复制旧版宽松完成判定。
- Android整帧写入默认沿用旧版 `writeNoResponse`，只有明确仅支持 `write` 才使用带响应写；设备ACK不再等待原生写API回调。取消普通请求时释放在途队列，阻止旧分片、探测和写模式回退干扰OTA。
- MTU改为尽力协商512；失败或无返回时保留原有写入容量并记录未知来源，不虚构512。已知容量不足仍阻断；设备 `0x52` 指定包长必须原样使用，超过整帧容量报错，不静默缩包或拆分 `0x53`。
- BLE与MQTT均在OTA期间暂停普通轮询并独占请求队列，保留Socket心跳；结束时恢复轮询、日志与帧间隔，并在 `finally` 恢复屏幕设置。保留既有Android仪表4KB边界300ms、超时降速及完成帧策略。
- 类型检查、12项定向测试和详情/参数页SFC编译通过，详见测试报告；未执行真机升级、提交、推送或部署。Android三条BLE链路及4G连续升级、弱信号和版本变化验收未完成，保持 `in_progress`。

## 2026-09-03 客户超时推进试验

- 本节替代前一轮同包超时重试与数据阶段额外等待策略。客户明确要求“即使ACK超时也继续下一包”；旧 `vendor.js` 仅能证实ACK驱动推进，本次超时推进是新增试验，不宣称逐字复制旧版。
- 共享引擎在首包、中途、末包450ms+220ms无ACK后发送下一包，不伪造确认进度；设备 `status=3` 请求下一包可继续、请求旧包有限补发，真实写失败/断连/取消不跳过。所有包尝试发送后可进入真实CRC32的 `0x54` 校验，仍只认 `status=0` 成功。
- 对齐旧版数据节奏：`0x52` ACK后立即发首包，BLE/MQTT OTA最小帧间隔、包间及4KB等待均为0，移除超时降速。保留仪表目标/查询/准备参数及既有完成300ms、BLE 800ms×8/6400ms、MQTT单发5s策略。
- 根据失败日志中持续增长的本地日志耗时，Boot期间改为最多6000条内存追加，finally集中发布/保存；复制可获取当前缓冲，debug/info不再重复输出console。BLE原生发送先于TX日志、ACK匹配先于RX日志，当前原生写失败立即释放pending，过期回调不影响后包。
- 13项本地回归、TypeScript和详情/参数SFC编译通过；实际传输代码模拟首/中/末包ACK丢失的推进间隔为670～673ms。600ms ACK配合两段50ms同步TX日志仍能接收，6100条追加无逐条存储/响应式更新。详见测试报告，不能替代真机成功率、弱信号与版本变化验收。
- 文档与看板维持 `in_progress`。无后端、数据库、固件、协议或依赖变更；未提交、推送、打包或发布，保留无关工作区改动。

## 2026-09-04 Flash页边界与设备游标收敛

- 复核 `_resources/ble-upgrade-log-20260904-2-failure.txt`：数据包1151已返回 `requested=1152`，客户端约5ms后发送包1152；`1152 * 64 = 73728 = 18 * 4096`，该包正是新Flash页首包。包1152无ACK后，9月3日试验逻辑继续发送1153至1162，设备始终保持 `requested=1152` 且无响应，最终BLE原生写失败。该证据与历史Android日志在包64、128页首失败，以及硬件工程师确认写整页约30～50ms无应答相互印证。
- 撤销9月3日“ACK超时继续下一包”和“数据ACK可不完整仍进入完成阶段”试验。`0x53` 继续使用450ms主窗口加220ms连续宽限；满670ms仍无ACK时重发完全相同的序号和数据，本地游标及进度不变，达到有界重试上限后失败。
- 将设备应答的合法 `requested` 收敛为唯一发送游标：状态机只按设备请求选择下一包，`status=3` 同样用于确认已收包或请求回退；主机不再因发送成功、超时或本地计数自行越过设备游标。全部数据必须确认到 `requested == packetTotal` 后才能进入 `0x54`。
- BLE与MQTT/4G统一恢复4KB页边界保护：设备ACK确认一整页后、发送下一页首包前等待300ms；同一页首包超时重试不重复等待，设备回退后重新跨越该边界则再次保护。两类链路数据阶段均设置 `minFrameIntervalMs=0`、`packetDelayMs=0`，普通包由ACK直接驱动且无额外固定等待；准备ACK后仍立即发送首包。
- 完成阶段保留真实CRC32及既有BLE 800ms×8/6400ms、MQTT单发5s窗口；成功仍优先要求 `0x54 status=0`。兼容路径窄化为直连BMS或仪表自身BLE、全部数据ACK完整、至少派发过一次 `0x54` 后发生明确原生设备断连；仪表透传BMS、普通超时、数据阶段断连、未完整ACK、MQTT/4G断连或非零状态均不得成功。
- 保留Boot日志有界内存与延迟落盘；每个 `0x53` 数据包保留一条包含 `seq/status/requested/RTT` 的紧凑结构化 ACK，删除 Boot 层重复的 `0x53` 完整十六进制记录，完整十六进制只保留首包、末包、4KB 边界包、同包重试和异常，避免日志桥接与响应式刷新再次挤占ACK窗口。
- 本轮不改后端接口、数据库、固件格式、Boot协议或依赖。9月3日试验记录作为失败历史保留，但已被本节取代；Android微信小程序/App三条BLE链路、4G链路、弱信号/弱网、iOS冒烟及升级后版本变化尚待真机验收，状态保持 `in_progress`。
- 本地回归已执行并通过：Boot时序、运行参数、BLE/MQTT实际transport、BLE整帧/MTU、页面OTA会话、日志精简、普通MQTT响应/wakeup/fjia2、轮询策略、仪表透传策略、TypeScript、详情页与参数页SFC编译及 `git diff --check`。上述结果仅覆盖静态与模拟环境，不替代真机验收。

## 2026-09-04 Android BLE原生写与通知恢复

- 复核 `_resources/ble-upgrade-log-20260904-3-android.txt`：Android仪表自身OTA在MTU 185、ATT容量182、75字节完整帧和RSSI -45条件下连续确认包0～191；包192位于第三个4KB新页首包，已等待约300ms，随后初发和5次约670ms同序重发均无可解析ACK。严格同包重发已生效，本次可排除MTU、分片、CRC、弱信号和超时跳包作为直接原因。
- 修正Android写能力选择：特征明确支持 `write` 时Boot帧显式采用响应写；仅不支持响应写时使用无响应写。两项能力明确false时Boot前失败，属性均缺失只作为 `legacy-unknown` 兼容无响应写；响应写返回 `10007` 时只对当前同一帧回退一次。
- 补齐原生写生命周期：ACK pending先于原生调用建立，原生success只用于诊断且不推进协议；当前请求fail立即失败，ACK后的迟到fail仅记录。300ms回调软超时不改变670ms ACK截止。Android通知特征明确可读时，在450ms无ACK处执行一次不延长总窗口的best-effort读取。
- 超时日志合并写模式、原生回调结果/耗时、RX字节数和限量Boot解析错误，正常数据包不增加重复日志。共享Boot状态机、450+220ms、300ms页保护、MTU整帧保护、MQTT/4G与iOS保持不变，不修改后端、数据库、固件格式、Boot协议或依赖。
- 客户端只能恢复Android GATT写丢失或Notify事件丢失；若响应写已原生成功而同序重发仍持续无RX，后续可靠性依赖Bootloader在Flash完成后ACK、对重复/旧序号始终返回当前 `requested`、回复 `0x54 status=0` 后再重启。Android六组真机连续20次及弱信号、版本变化仍待验收，状态保持 `in_progress`。
