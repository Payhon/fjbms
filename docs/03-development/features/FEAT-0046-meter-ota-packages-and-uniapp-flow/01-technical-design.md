# FEAT-0046 仪表 OTA 升级包与 UniApp 独立升级链路 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-09-12
- related_feature: FEAT-0046
- version: v0.1.9

## 2026-09-12 动态 ACK 设计（取代历史固定450+220与完成连发策略）

- 复用bootRequest与现有数据/完成循环：0x50～0x52使用OTA内部超时重试包装，独立版本查询API不变；0x53既有循环按首次800/重发450选择timeoutMs，无额外宽限。
- 页面封装透传每次timeoutMs，移除450ms硬上限；共享恢复预算3次，不对数据循环再套重试层。
- 完成循环最多4次，首次5000ms、重发450ms，仅ACK超时继续；删除重复writeFrame定时器和重发sleep，保留首次300ms、CRC与成功证据。
- BLE探测仅在graceMs大于0时调度，普通请求不受影响。无新依赖/对外API；新时序与取消、页边界、兼容条件使用可控时钟及transport回归验证。

## 2026-09-10 BLE 会话恢复设计

- transport 提供内部断连订阅；先保留 pending 的原生错误/完成上下文，再清理并通知。路由解绑、缓存删除按对象身份核对。
- 缓存统一关闭入口与按设备关闭 Promise：成功或明确无连接解除屏障；失败/回调缺失不放行同设备连接。退出仍有界等待并释放全局协调锁。
- 恢复放在详情会话管理，由 OTA 子组件异步回调；保留原 client/仪表MAC/设备ID/升级类型/结果。30秒总预算最多两次，恢复不启动普通轮询，不写 Boot 准备或数据命令。
- 页面销毁/设备切换使恢复代次失效并取消连接、读取；恢复成功才绑定新 client 并恢复 Tab 轮询，失败清理候选连接并保持离线。普通断连不触发自动OTA恢复。
- 独立恢复提示和读回版本，保留原升级成功/失败。复用既有连接、状态读取和版本查询；不新增对外协议、依赖或全局适配器重置。

## 1. 数据与接口
- `ota_upgrade_packages` 新增 `device_kind int2 not null default 1`。
- `/api/v1/ota/package`
  - `GET` 增加 `device_kind` 查询参数；未传时默认按 BMS 查询，兼容现有任务页与批量 OTA 页面。
  - `POST/PUT` 增加 `device_kind`；`device_kind=2` 时仅校验 `name + package_url`，其余 BMS 字段由服务层忽略或回填兼容值。
- `/api/v1/app/battery/ota/meter-packages`
  - 基于 APP 租户上下文返回全部 `device_kind=2` 的升级包，按 `created_at DESC` 排序。
  - 对已登录 APP 接口，租户解析优先级为 JWT `claims.TenantID`，其次 `X-TenantID` 请求头，最后回退默认租户。
  - 当 header 与 claims 不一致时，以 claims 为准，并记录告警日志。
  - 查询兼容租户私有包与公共包（`tenant_id IS NULL`）。
- `/api/v1/app/battery/ota/check`
  - 保持原请求/响应结构；带 `device_id` 的直接 BMS 检查路径不变。
  - 仪表临时会话不传 `device_id`，传现场读取的 `item_uuid/model/version`。服务端先按当前租户 UUID 补齐型号ID与批次；UUID未登记时仍可直接命中 UUID 约束包。
  - 缺少型号ID时，将硬件型号按当前租户、大小写不敏感解析为 `battery_bms_models` ID集合；选包仍按 UUID、型号、批次约束得分和版本门槛执行，最后允许通用 BMS 包兜底。

## 2. 后台管理端
- 升级包管理页使用双 TAB：
  - `BMS 升级包` 保持现有字段与列表列。
  - `仪表升级包` 仅展示名称、说明、固件文件、创建时间。
- OTA 任务页与电池列表拉取升级包时显式带 `device_kind=1`，避免误取仪表包。

## 3. UniApp 升级流程
- 设备详情页通过 `ble_mac` / `status.identity.bluetoothMac` 调用 `isMeterMac()` 判断仪表。
- 仪表设备：
  - 关闭现有 OTA Cell、版本红点与自动检查。
  - 参数页新增“仪表升级”卡片，用户先打开包列表，再选择固件，再点击“开始升级”。
  - 包列表数据源为 `/api/v1/app/battery/ota/meter-packages`。
  - 蓝牙已连接但未建立 BMS 透传时保留 `client` 与蓝牙连接，不阻断仪表升级入口。2026-08-31 起按 FEAT-0041 v0.5.0：10 秒只结束遮罩，仪表盘/电芯页继续低频串行读取；参数/历史页及 OTA 独占期间仍暂停，旧“超时后停止轮询”策略不再适用。
  - Android 扫描进入仪表详情时同时携带扫描得到的 BLE `deviceId`；连接层优先使用该候选，并过滤与目标 AA MAC 不兼容的 MAC 型候选，防止历史 AC 设备任务串入仪表会话。iOS 扫描得到的 UUID 型 `deviceId` 不参与 MAC 字符串兼容过滤，允许作为直连候选使用。
  - 蓝牙扫描页使用扫描会话 ID 隔离过期回调；停止扫描时立即关闭设备发现监听和 UI 动画状态，扫描时长超时后自动停止并恢复“开始扫描”按钮。
  - BLE 连接阶段调用方保留超时出口：Android 连接等待6.5s、iOS等待9s。同一MAC的旧连接任务8s仍未结束时，不再替换并并发建连；原生create回调迟到时必须先结束旧create、再close，close成功或明确无连接后才能释放同设备屏障。全局扫描租约在取消时释放，原生回调缺失只隔离该设备，不重置全局适配器。
  - 确认升级后直接下载 `package_url` 并调用 `bootOtaUpgrade()`；升级写包目标地址固定为 `0xFC`。
  - 依据真实仪表升级日志与蓝牙链路约束，Boot 查询 `0x50` 使用广播目标地址 `0x00`，不发送 `0x51` 进入 Boot；蓝牙仪表升级时 `0x52` 的第二段 4 字节参数固定为 `9600`。
  - BLE/MQTT 透传层对 Boot 应答做地址兼容：仪表 OTA 虽然下发目标地址为 `0xFC`，但设备回包源地址仍可能为 BMS Bootloader 地址 `0x01`，transport 必须接受该特例。
  - 数据 ACK 超时后，transport 必须清理本次残留 pending，再由升级引擎使用完全相同的序号和数据重发；不得因为超时推进本地游标。`0x53` 回包 `status=5` 按“固件包大小与设备不一致”展示。
  - 全部移动端OTA的0x50～0x53首次800ms、最多3次超时重发各450ms；bootAckGraceMs=0。页面透传单次timeoutMs，禁用替代写二次重试，普通读取策略不变。
  - Android BLE 在 Boot 前尽力请求 512 MTU；明确返回值才更新 `MTU-3` 写入容量。API 不支持、失败或成功无数值时保留原有容量并记录 MTU 未知，不再一刀切阻断或假定 512。明确低于 78 仍阻断；`0x52` 指定的包档位不得被本地 MTU 裁小，超容量在首个数据包前失败。
  - 独占 OTA 中 `0x53` 必须一次 BLE 写入，超容量以 `boot_ble_frame_exceeds_mtu` 中止，不做20字节分片。Android写能力按明确属性选择：`write=true` 时所有Boot帧显式 `writeType='write'`，即使同时支持无响应写；仅 `write!==true && writeNoResponse!==false` 时使用 `writeNoResponse`。`writeNoResponse=false` 且 `write!==true` 时Boot前失败；两项均缺失时以 `legacy-unknown` 标记后兼容无响应写。iOS写模式保持原策略。
  - Android每次Boot写入先建立ACK pending和本次800/450ms计时，再调用原生API。原生 `success` 只证明GATT写调用完成，不推进Boot游标；有效ACK仍是唯一协议成功依据。当前pending上的非能力类原生 `fail` 立即失败，ACK已到后的迟到fail仅记录。Android响应写返回 `10007/property not support` 时只对同一帧回退一次无响应写并在本会话沿用，iOS不进入该回退；原生回调300ms未完成只标记软超时，不能替代或延长Boot ACK窗口。
  - 当前OTA宽限为0，不调度Android超时读探测；transport仅保留显式非零宽限调用的原探测能力，不用于本轮OTA。
  - BLE/MQTT 在匹配地址、命令和CRC后，以 `0x53` 应答中的合法 `requested` 作为唯一发送游标。`status=0` 表示当前写入成功，`status=3` 表示设备要求按返回游标纠正序号；两者都不能由主机自行加一替代。游标必须位于 `0..packetTotal`，回退、重新准备与超时共用最多3次无进展恢复预算，只有设备确认水位前进才重置预算；非法游标、设备明确拒绝和恢复耗尽立即失败。
  - 9月3日“满670ms后跳到下一包”的试验分支已撤销。首包、中途、末包首次800ms或重发450ms仍无ACK时，记录同包重试并重新发送相同 `0x53`；本地游标、确认水位和进度均不变。原生写失败、断连、取消、解析错误或设备明确拒绝仍直接失败，不能伪装为ACK超时。
  - Boot 接收器跳过普通 `7F55` 帧头及非 Boot 命令，对坏 CRC/错误帧尾在同一批数据中继续扫描；普通迟到回包、坏帧与有效 ACK 粘包时不能提前结束解析或误等待一个虚构的大包。
  - `0x53` 进度只在有效ACK后按设备 `requested` 更新；发送、超时、同包重发和游标回退期间不预增进度。OTA Boot阶段保持屏幕常亮，并在 `finally` 中恢复；诊断日志记录MTU、ATT payload、帧长、写模式、原生发送时刻、ACK RTT、设备游标、同包重试/回退次数和升级前RSSI。
  - 以已确认字节数计算Flash页边界：`confirmedBytes = min(requested * packetSize, totalSize)`。当 `confirmedBytes > 0`、`confirmedBytes % 4096 == 0` 且 `requested < packetTotal` 时，在发送下一页首包前等待300ms；同一页首包因超时重发时不重复等待，设备游标回退后重新跨越该边界时再次保护。普通包不增加固定包间延迟，BLE与MQTT/4G共用该边界保护。
  - 蓝牙BMS与蓝牙仪表OTA共用完成阶段边界策略：必须由设备游标确认 `requested == packetTotal`，随后等待300ms发送首个 `0x54`；首次等待5秒，超时最多重发3次、每次450ms，无ACK时发送时刻为 `0/5000/5450/5900ms`，6350ms耗尽。发送使用原固件真实CRC32，不照搬旧版零CRC字段。
  - 本轮BLE与MQTT/4G数据阶段均设置 `minFrameIntervalMs=0`、`packetDelayMs=0`，普通包无额外固定等待并由ACK直接驱动。两类链路均启用300ms的4KB边界等待，不再采用“超时跳包”，结束后恢复普通通讯原间隔。
  - BLE/MQTT OTA 在进入 Boot 前开启独占通讯会话：取消在途普通读取及 MQTT 唤醒补发，最多等待 1.2s 排空既有队列；入队与实际发送前均拦截非 Boot 请求。详情页所有会话类型在 OTA 时暂停轮询，不能被 4G 参数页 10 秒保活重新启动；MQTT WebSocket ping 保留。`finally` 释放独占、清理计时器并恢复当前 Tab 策略。
  - 蓝牙BMS与蓝牙仪表及MQTT/4G的 `0x54` 使用首次5000ms、最多3次450ms超时重发，不启用连发定时器或iOS替代写模式重试，也不接受残留 `0x53` ACK 作为完成应答。匹配的 `status=0` 立即取消剩余补发并成功，非零状态立即失败。仅直连BMS或仪表自身BLE在全部 `0x53` 已确认、至少派发过一次 `0x54`、且随后收到明确原生设备断连错误时允许按设备重启兼容收敛；仪表透传BMS、单纯窗口超时、写入前断连、数据不完整和MQTT/4G断连均失败。
  - 全部移动端 OTA 收到有效 `0x52` 应答后立即发送首个 `0x53`；重新初始化补发 `0x52` 时同样不增加300ms等待。数据阶段结束到首个 `0x54` 仍为300ms。MQTT/4G与BLE共用首次5000ms、重发450ms的完成策略。
  - 仪表 OTA 保留专用准备参数：`0x50` 广播查询、跳过 `0x51`、`0x52` 固定9600；标准BMS的进入Boot等待200ms不变，不盲目复制旧UI缺失的前置组帧。
  - 开发者模式下，仪表升级卡片下方显示“升级调试日志”：端上记录选包、固件下载、`0x50/0x52` 前置、首包预览、关键 ACK、失败错误对象与成功收敛证据；支持复制与清空，仅做本地展示，不上传后端，不改变升级协议。
  - Boot期间日志追加到最多6000条的普通内存数组，不逐条重建响应式列表或同步全量落盘。正常 `0x53` ACK维持单条紧凑记录；首包、末包、4KB边界、重试和异常才保留完整十六进制。Android每次尝试记录 `cmd/seq/attempt/writeType/nativeOutcome/nativeRtt`，但正常成功不增加逐包重复日志；重试/超时汇总RX chunk/字节数、非法Boot候选和最后解析错误。正常成功/失败/取消在finally统一发布和保存，复制读取当前内存；强杀进程可能丢失未保存日志。
  - 最新Android日志证明页保护后仍可能出现至少4秒持续静默：包0～191正常，包192首发及5次同包重发无可解析ACK。当时客户端用响应写、原生回调和一次读取探测覆盖可恢复的下行/Notify丢失，但不能在设备持续静默时猜测游标。Bootloader后续必须保证Flash提交后ACK、重复/旧序号始终回当前 `requested`、`0x54 status=0` 后再重启。
- 仪表透传 BMS：
  - 在仪表升级卡片下方显示独立“BMS升级”卡片；仅限 `bluetooth + instrument + AA仪表`，状态未包含 BMS 型号/版本时卡片可见但按钮禁用。
  - 点击后暂停轮询并限时调用 `readUuid()`；UUID失败只记录日志并降级到型号/版本，两类身份均缺失时阻断，不在页面加载阶段自动检查。
  - 匹配确认后以显式目标 `0x01` 执行标准 BMS `0x50/0x51/0x52/0x53/0x54`，不套用 `0xFC` 仪表专用参数；仪表自身和BMS升级共享运行互斥锁。
  - 普通轮询在所有取消、失败、成功路径恢复；Boot独占会话由 `runBootOtaUpgrade()` 的 `finally` 释放。
- BMS 设备继续沿用现有 `ota/check -> need_upgrade -> bootOtaUpgrade()` 链路。

## 4. 测试策略
- `cd backend && go test ./internal/service/...`
- `cd frontend && pnpm build`
- `cd fjbms-uniapp && pnpm exec tsc --noEmit`
- Android BLE transport定向覆盖写能力矩阵、`10007`同帧回退、ACK/原生回调竞态、零宽限不探测、800/450ms同序重发及超时RX诊断；MQTT/4G和iOS行为做回归断言。
- 手工验证：
  - 后台双 TAB 查询/新增/编辑/删除
  - BMS 批量 OTA 页面仍只看到 BMS 包
  - 蓝牙仪表详情页选包、确认、升级进度与失败提示
  - 仪表透传 BMS 卡片可见/禁用状态、UUID成功与型号降级、目标 `0x01` 首帧、失败恢复和三条 OTA 链路回归
