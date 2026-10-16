# FEAT-0049 BMS 4G 移动端云端详情链路 - 实现日志

- status: in_progress
- owner: payhon
- last_updated: 2026-10-09
- related_feature: FEAT-0049
- version: v0.2.12

## 2026-10-09 生产发布（后端 + Web）

1. 发布范围
   - 仅替换生产后端二进制并重启 `fjbms-backend`，随后原子替换生产 Web 静态目录。
   - 未同步后端配置、SQL、BMS Bridge，未构建或发布 UniApp，也未提交或推送代码。
2. 发布结果
   - 后端本地与线上 SHA-256 均为 `413657d05e7c35c907005fd017c08b098dfc5b15ad147d686cafb426ca2ceccc`。
   - Web `index.html` 本地、服务器与公网 SHA-256 均为 `61b0d346db255801157ced4c563b271a07a9fd4223a93df42d509f0293bf667a`；共享查看和 owner transport 两个产物也分别与公网校验一致。
   - `fjbms-backend` 为 `active`、`NRestarts=0`，服务本机及公网 `/health` 均返回 HTTP 200，重启后日志未命中 `panic/fatal/error`；匿名访问共享快照接口返回预期 HTTP 401。
3. 回滚备份
   - 后端：`/www/fjia/backups/fjbms/backend/backend_20261009_212454_pre_shared_view.bin`。
   - Web：`/www/fjia/backups/fjbms/frontend/frontend_20261009_212454_pre_shared_view.tar.gz`。

## 2026-10-09 单透传会话、多端共享查看

1. 保留设备级唯一透传 owner
   - 后端 Redis owner、45 秒 TTL、session 匹配释放及非 owner 拒绝逻辑不变。
   - occupied 提示由“其他账号”改为“其他终端”，避免同账号后台/手机并行查看时误导。
2. Web owner 上报共享快照
   - Web Transport 声明 `mqtt_socket_owner_v1`，等待并保存 `socket_ready.session_id`；`socket_occupied/socket_error` 在建立 BMS Client 前失败，旧后端仍保留 1.2 秒兼容窗口。
   - 后台每次完整 `readAllStatus()` 成功后复用既有 `interactive-snapshot` 接口；单 in-flight、latest-wins 队列只保留最新状态，断开时清理未发送值。
   - 后台快照上报使用静默请求，不清除或弹出业务操作消息；上报失败不影响当前 owner 本地实时显示。
3. 多端共享查看
   - 后端保存主动读取快照后复用当前遥测 Redis/WebSocket 事件广播 `bms.mqtt_interactive_snapshot`。
   - Web 当前遥测首次查询与 WebSocket 订阅加入该键，显示优先级为本地实时状态 > owner 共享快照 > 普通 `bms.snapshot`。
   - Web 仅在底层 Socket 已确认断开时清理旧本地实时状态，使新 owner 的共享快照能够接管；普通读取超时仍保留最后实时值并继续原重试行为。
   - 手机端继续复用原 APP 当前遥测 5 秒轮询和原子快照优先级，仅将 occupied 文案调整为“共享/云端只读”。
4. 未改范围
   - 未新增数据库字段、依赖、MQTT Topic 或第二条设备透传；参数、控制和 OTA 继续仅 owner 可用。

## 2026-09-12 OTA动态超时兼容边界（当前生效）

- MQTT/4G明确纳入新时序：0x50～0x53首次800ms、最多3次450ms重发；0x54首次5000ms、最多3次450ms重发。原单发完成与670ms数据窗口由此取代。
- 控制命令与数据重试不叠加；0x50及4G的0x51耗尽超时后继续兼容保留；0x52/0x53耗尽失败，不得进入完成。只有实际完成ACK可使4G升级成功。
- 保留300ms页保护、ACK游标及完整数据门槛。Socket transport、普通读取/唤醒/轮询、云端接口、连接恢复与数据库不变；BLE恢复不扩展至MQTT。
- 无依赖或对外API变更，不提交/推送；真机4G连续20次、交替版本及弱信号验收待完成，保持in_progress。历史日期记录不代表当前时序。


## 2026-09-10 BLE OTA 恢复兼容边界

- FEAT-0046新增的关闭屏障、原生断连订阅和30秒/最多两次恢复仅应用于BLE。共享详情页的MQTT连接、云端回退、参数轮询、后台命令转发及OTA协议策略不作调整。
- MQTT/4G仍使用670ms同包重试、300ms页保护、完整数据ACK门槛和单发5秒完成窗口；既有工作区修改保留，本轮未再次修改MQTT transport或共享Boot引擎。
- Boot/运行参数/transport及MQTT响应匹配、唤醒、fjia2和页面会话回归通过；新断言确认MQTT不会进入BLE恢复。真机4G/App及iOS/Android冒烟仍待完成，保持in_progress。
- 发布和回滚只涉及FEAT-0046本轮移动端差异，无后端/数据库/接口/依赖变更；本轮不提交、推送或部署。

## 2026-04-27
1. 新增 APP 当前遥测接口
   - `GET /api/v1/app/battery/current-telemetry/:device_id`
   - 返回当前遥测键、最后上报时间、在线状态和可解析的 `bms.snapshot`
2. 调整 UniApp 设备详情连接策略
   - 4G-only 设备跳过 BLE/MQTT 主动读链路
   - 使用云端当前遥测合成详情页 `BmsStatus`
   - 保留 BLE-only 设备原逻辑
3. 优化电芯 Tab 空态
   - 未收到 `cell.voltagesMv` 时显示“未收到电芯明细数据”
   - 不根据最高/最低/压差摘要伪造单体列表
4. 修复 4G 动态电芯帧到当前遥测的结构化链路
   - `bms-bridge` 在 `report.startAddress == 0x0141` 时基于已知 `seriesCount`、`cellTempCount` 解析动态区。
   - 新增输出 `cell.voltagesMv`、`temperature.cellTempsC`、最高/最低单体电压索引、单体电压和、平均单体电压等扁平字段。
   - 元数据优先来自 `0x0100` 完整状态帧缓存，缓存缺失时回查当前遥测/属性；仍缺失则只保留原始寄存器，不猜测数组边界。
   - 局部动态区帧不生成 `bms.snapshot`，避免覆盖完整状态快照。
5. 更新后台 BMS 面板云端展示
   - 当前遥测订阅键增加 `cell.voltagesMv`、`temperature.cellTempsC`、`electrical.cellVoltageIndex.*` 等字段。
   - 电芯 Tab 在无 `bms.snapshot.cell.voltagesMv` 时回退使用当前遥测 `cell.voltagesMv`。
   - 支持复杂遥测值以 JSON 字符串落库后的数组解析。
6. 明确数据源差异
   - 通讯调试管理读取 `bms_bridge_comm_logs` 原始报文链路。
   - 后台/移动端 BMS 面板读取当前遥测和可选 `bms.snapshot`，需要 bridge 规则发布结构化字段后才可展示电芯列表。
7. 优化后台 Web 端 4G 设备详情交互
   - 4G 设备进入 BMS 面板默认只加载/订阅云端遥测，不再自动发起参数直连和主动 `readAllStatus()`。
   - 面板状态拆分为 `MQTT上报在线`、`云端订阅`、`参数直连/APP中继` 三类，避免参数通道失败被误读为设备离线。
   - 4G 设备参数通道改为用户手动点击“连接参数直连”后建立，仅用于参数读写，不作为设备在线判断依据。
   - 云端遥测 WebSocket 断开后自动重连；“刷新云端”同时刷新电池基础信息、当前遥测和历史图表。

## 2026-04-29
1. 修复 UniApp 扫码添加已绑定 4G 设备误报失败
   - `provision/info` 返回 `is_bound=true` 且有 `device_id` 时，移动端直接进入设备详情页，不再重复调用 `provision/bind`。
   - 兼容旧后端重复绑定返回 `device already bound to current user` 的情况，移动端按幂等成功处理并跳转详情。
2. 修复 UniApp 4G 设备详情当前遥测兼容链路
   - 优先请求 `GET /api/v1/app/battery/current-telemetry/:device_id`。
   - 当生产后端暂未提供该 App 专用路由导致 HTTP 404/reject 时，降级请求既有 `GET /api/v1/telemetry/datas/current/:device_id`。
   - 将通用当前遥测列表转换为详情页统一的 `current` map，并基于最新遥测时间给出 `is_online` 兼容值。
   - 云端状态合成兼容旧键名 `cellVoltagesMv`、`cellTempsC`、`cellVoltageHighestIndex`、`cellVoltageLowestIndex`。
3. 切换 4G 设备详情为 MQTT Socket 透传实时读取
   - 后端 `/api/v1/app/battery/socket/ws` 首包继续接收数据库 UUID 做鉴权和可见性校验。
   - 鉴权通过后从设备详情取 `devices.device_number` 作为 MQTT Socket Topic 标识，订阅 `device/socket/tx/{device_number}`，发布 `device/socket/rx/{device_number}`。
   - `device_number` 为空时直接拒绝初始化，不回退使用数据库 UUID，避免前端误把路由 UUID 当硬件 Topic。
   - UniApp 4G/4G+BLE 设备进入详情后优先建立 Socket 透传并用 `BmsClient.readAllStatus()` 实时刷新；透传失败时降级使用主动上报当前遥测。
   - Web 端 BMS 面板进入 4G 设备详情后自动建立 Socket 透传；手动按钮保留为重新连接/断开实时透传。
   - UniApp/Web Socket Transport 同时支持普通 BMS `0x03` 读寄存器帧和云平台 `SOCKET_READ=0x0F` 读指令，复用 BMS 解析逻辑。
   - 前端状态显示区分为 `MQTT透传实时`、`主动上报兜底`、`离线/无数据`。
4. 修复 4G Socket 读响应帧长度解析
   - 生产 WebSocket 实测目标设备 `36011161145053593437373030124930` 已能通过 `/api/v1/app/battery/socket/ws` 返回 `0x0F` 透传帧。
   - 实测 `0x0F` 响应中的 `byteCount` 为数据字节数，不是寄存器数量；移动端和 Web 端解析层不再对 `SOCKET_READ` 执行 `byteCount * 2`。
   - UniApp `parseFrame` 保留 `0x0F` 数据区中的 `startAddress/quantity` 头，由 `BmsClient` 的 `parseSocketReadPayload()` 统一校验并剥离，避免重复剥离后触发地址不匹配。
   - 修复后 `0x0F` 响应可进入同一套 BMS 寄存器解析链路，避免移动端日志中的 `[socket] drop invalid frame` 和随后超时降级。
5. 修复 4G Socket 轮询阶段超时
   - 生产复测发现目标设备对 `0x0100` 固定区读取可能 4~7 秒才返回，原 2500ms 超时会提前进入下一轮请求。
   - 目标设备对小范围读取可能返回整段区域，例如读 `0x0100, qty=1` 返回 `0x0100, qty=54`；客户端改为缓存 `0x0F` 响应整段寄存器，并按请求范围取交集。
   - 动态区 `0x0141` 响应可能短于包含身份字符串/MAC 的完整计算范围；客户端接受已有动态数据并对缺失部分保持 0 填充，保证仪表盘和电芯数据优先可显示。
   - UniApp/Web 4G Socket 默认请求超时调整为 10000ms，并修复串行请求队列在一次超时后持续复用 rejected Promise 的问题。
6. 修正 4G Socket 参数配置读取路径
   - 生产参数寄存器无响应时目标设备已离线，不能据此认定 4G Socket 不支持参数配置寄存器。
   - 检查发现 4G Socket 请求响应匹配只校验 `0x0F` 与地址方向，未校验请求寄存器区间；设备主动上报的 `0x0100/0x0141` 状态帧可能误唤醒 `0x0400` 参数读取请求，随后在客户端解析阶段因地址不匹配被置空。
   - UniApp/Web 透传 Transport 增加 `SOCKET_READ` 请求区间匹配，只有响应区间与请求区间存在交集时才作为该请求响应；仍保留小范围请求接受整段响应的兼容能力。
   - UniApp 参数设置页撤回“4G 透传不支持参数配置”的过滤和提示，在线设备会继续按权限读取参数寄存器；离线或超时仍按无连接/无数据处理。

## 2026-04-30
1. 修正 4G MQTT 透传功能码选择
   - 根据移动端真机反馈和协议确认，4G MQTT 透传只是通讯通道变化，普通 BMS 寄存器仍完全遵循 BLE BMS 帧协议，读寄存器功能码应为 `0x03`。
   - 云平台读指令 `SOCKET_READ=0x0F` 仅适用于 4G 模块专有寄存器 `0x0900~0x0923`，例如经纬度、RSSI、IMEI、ICCID、4G 模块软件版本。
   - 修正 UniApp/Web Socket Transport：不再把所有普通 `0x03` 读请求统一转换为 `0x0F`；仅当请求区间完全落在 `0x0900~0x0923` 时才自动转换。
   - 保留 `PARAM_DEF_BY_KEY` 中 4G 专有参数的 `functionCode: SOCKET_READ` 与 `targetAddress: 0xFA` 声明，普通参数配置页读取 `0x0400` 等地址时恢复为 `0x03` 透传。
2. 优化参数设置面板读取性能
   - 新增 `BmsClient.readParamsByKeys()`，按参数定义将同一功能码/目标地址下的参数合并为连续寄存器范围后批量读取。
   - UniApp 参数设置面板展开分组时不再逐项调用 `readParam()`，改为一次批量读取并批量写入 `paramValues`。
   - Web BMS 面板直连模式同样改为批量读取，BLE 与 4G MQTT 透传共享同一优化；Web APP 中继 fallback 暂保留单参数命令路径。
   - 典型分组如单体设置、总压设置从十几次串行读寄存器减少为少量连续范围读取，避免值一项一项缓慢显示。
3. 优化移动端等待态
   - UniApp 设备详情新增 `bmsDataLoading`，连接成功但首帧 BMS 实时状态尚未返回时，仪表盘改为显示中英文加载提示，避免短暂展示空白/零值数据。
   - 参数设置基础分组调整为首次点击时先显示右侧加载图标，等 `readParamsByKeys()` 返回后再展开列表，并把图标切回向上箭头。
   - 加载态在首帧成功、离线断开、轮询暂停或旧板仪表透传不可用时会清理，避免残留转圈状态。

## 2026-05-25
1. 优化移动端 4G 连接状态展示口径
   - UniApp 设备详情顶部连接胶囊在 `connType=mqtt` 时统一显示 4G 图标与“已连接”。
   - 不再向终端用户展示 `MQTT透传实时`、`主动上报兜底` 等技术链路文案；内部 `dataSourceMode`、Socket 透传和主动上报兜底逻辑保持不变。
   - 蓝牙连接、离线、连接中状态维持原有展示逻辑。

## 2026-06-04
1. 优化移动端 4G 详情首屏响应
   - 4G/4G+BLE 设备详情加载基础信息后，立即请求 `current-telemetry` 作为首屏快照，后台继续连接 MQTT Socket 透传。
   - Socket 切换期间允许保留当前遥测合成的 `status`，避免首屏快照被 `disconnectAll()` 清空回加载态。
   - `current-telemetry` 若晚于实时 `readAllStatus()` 返回，不再覆盖实时数据源。
   - 4G Socket 建连后移除 `readUuid()` 预读，直接进入后台 `readAllStatus()` 轮询，减少首帧前额外往返。
2. 补齐 APP MQTT Socket 路由
   - 后端路由注册 `GET /api/v1/app/battery/socket/ws`，使已实现的 `ServeBatterySocketByWS` 可被移动端详情与 4G OTA 使用。
3. 支持 4G BMS OTA 透传
   - BMS OTA 入口在 `connType=mqtt` 时复用现有 BMS OTA 包检查、固件下载与 BOOT 升级流程。
   - 4G BMS OTA 使用 MQTT Socket Transport 的 `request()` 发送 BOOT 帧，BMS 目标地址仍为 `0x01`，仪表设备仍为 `0xFC`。
   - MQTT OTA 增加更长 ACK/收尾超时、最小帧间隔、包间延迟、页边界延迟和自适应降速参数，适配 4G/MQTT 透传时延。
4. 加固 MQTT Socket BOOT 响应匹配
   - `UniMqttSocketBmsTransport` 兼容 finalize `0x54` 收到 `0x53` ACK 的 BOOT 回包。
   - 仪表 BOOT 源地址兼容 `0xFD`，保持与蓝牙 OTA 解析口径一致。

## 2026-06-05
1. 修复 4G BMS OTA BOOT 阶段超时
   - 生产 `bms_bridge_comm_logs` 确认目标 4G BMS 对 `0x50` 版本查询约 3 秒返回，原移动端 `0x50` 固定 3000ms 超时会提前清理 pending，导致升级失败。
   - 仅在 `connType=mqtt` 的 BMS OTA 运行参数中放宽 BOOT 查询、进入 Bootloader、准备和数据包 ACK 超时；BLE BMS 和仪表升级保留原参数。
   - MQTT BMS OTA 对 `0x51` 进入 Bootloader 的 timeout 支持继续执行到 `0x52`，适配 4G 透传下进入 Bootloader 可能无 ACK 或 ACK 晚到的情况；非 timeout 错误仍按失败处理。

## 2026-06-08
1. 增加 4G BMS MQTT Socket 设备级 owner 保守互斥
   - 后端 `/api/v1/app/battery/socket/ws` 在鉴权和设备可见性校验通过后，使用 Redis `bms:mqtt_socket:owner:{device_id}` 执行 `SET NX` 抢占实时透传 owner。
   - owner value 记录 `session_id/user_id/tenant_id/device_id/device_number/platform/last_seen_ts/expires_at_ts`，TTL 为 45 秒。
   - `ping` 和任意下行发布请求会刷新 owner TTL；WebSocket 关闭时只删除当前 `session_id` 匹配的 owner。
   - Redis 不可用或设备已被其他会话占用时保守拒绝新的实时透传连接，不踢掉旧连接。
2. 增加 Socket 控制消息兼容协议
   - 新移动端首包声明 `features:["mqtt_socket_owner_v1"]`。
   - 新后端仅对声明 feature 的客户端发送 `socket_ready/socket_occupied/socket_error` JSON 控制消息。
   - 未声明 feature 的旧客户端成功连接时不收到 `socket_ready`；占用失败时仍返回纯文本错误并关闭。
3. UniApp 4G 详情 occupied 只读降级
   - `UniMqttSocketBmsTransport.connect()` 等待 `socket_ready`，1.2 秒无控制消息时兼容旧后端继续连接。
   - Transport 忽略 `pong`，识别控制消息，occupied 时抛出 `MQTT_SOCKET_OCCUPIED`，并在 ready 后每 15 秒发送 `ping` 保活。
   - 详情页捕获 occupied 后自动切换到云端上报只读模式，顶部仍显示 4G，同时展示“实时连接被占用，当前显示云端上报数据”轻提示。
   - 参数配置、虚拟容量写入和 BMS OTA 在 occupied 只读模式下统一显示专用 toast，不再发实时透传指令。

## 2026-06-10
1. 优化 4G BMS OTA 数据包传输节奏
   - 仅在 `connType=mqtt` 的 BMS OTA 分支启用快速模式，将常规 `0x53` 包间固定等待降为 `packetDelayMs=0`、`minFrameIntervalMs=40ms`、`pageBoundaryDelayMs=100ms`。
   - 保留超时后的自适应降速参数，出现 ACK timeout 后仍切回更保守的包间与页边界等待。
   - BLE BMS、蓝牙仪表 OTA 和 occupied 云端只读拦截逻辑不变。
2. 增加 APP/后端 OTA 链路埋点
   - UniApp 记录 4G BOOT runtime options、每个 `0x53` 包的 APP 侧 RTT、ACK requested、尝试次数和当前快/慢模式参数。
   - WebSocket Transport 记录 Boot 请求的最小帧间隔等待、请求总耗时和响应帧摘要。
   - 后端 `/api/v1/app/battery/socket/ws` 对 Boot 帧记录 APP 下发到 MQTT 的 publish wait、MQTT 回包写回 WebSocket 的 lock/write/elapsed 耗时。
3. 加固 MQTT Socket BOOT 收包
   - Boot 收包扫描增加最大帧长保护，遇到普通 BMS 帧中的 `7F 55` 或异常长度候选时丢弃错误候选，避免真实 ACK 被卡在缓冲区后触发长超时重发。
4. 增加 Debug 模式 OTA 日志浮层
   - 扩展移动端 OTA 调试日志为通用 `ota-debug`，支持 BMS OTA、4G BMS OTA、仪表 OTA 和 Socket/BOOT 日志统一记录。
   - Debug 模式下 OTA 升级弹窗右上角显示日志查看图标，默认不展开；点击后展示深色浮动日志层，可滚动查看完整升级日志。
   - 浮层支持复制完整日志文本和清空日志；普通模式不显示入口。
   - OTA 运行期间临时将 Transport logger 指向 OTA logger，使 APP 端 `[socket] boot request timing` 等控制台日志同步进入界面日志。

## 2026-06-11
1. 优化 Debug 模式 OTA 日志浮层展示
   - 将 OTA 调试日志面板从 OTA 升级 `u-popup` 内部移到页面级 fixed 浮层，避免被升级弹窗内容容器裁剪。
   - 日志正文高度改为按当前窗口、安全区和浮层头部操作区动态计算，小屏设备可通过浮层内滚动查看完整日志。
   - 点击浮层外侧仅关闭日志层，不关闭 OTA 升级弹窗；复制、清空和关闭按钮行为保持不变。

## 2026-06-12
1. 后端加固 4G BMS OTA ACK 链路诊断
   - `/api/v1/app/battery/socket/ws` 在 MQTT `device/socket/tx/{device_number}` 收到 BOOT retained 消息时不再转发给 APP，避免旧 retained ACK 污染当前 OTA 会话。
   - WebSocket 会话内增加 BOOT 轻量追踪状态，仅用于日志记录最近下发 `0x53` 包号、最近 ACK requested、包重发、ACK 间隔、ACK 到云端后下一包下发间隔。
   - 当 ACK 间隔或 ACK 对应下发后的回包耗时超过 2 秒时，后端输出 `bms mqtt socket boot uplink slow ack` 警告，便于区分 4G 模块/蜂窝上行延迟和后端发布耗时。
   - 当 ACK 已到云端但下一包进入后端下发耗时超过 2 秒时，输出 `bms mqtt socket boot downlink slow after ack` 警告，用于排查 APP/WebSocket 侧停顿。
   - MQTT topic、QoS、owner 互斥、WebSocket 控制消息和非 BOOT 实时透传行为保持不变。
2. 增加 4G BMS 休眠唤醒查询补发
   - `UniMqttSocketBmsTransport` 记录最近一次有效响应时间；从未收到响应或距离上次响应超过 30 秒时，首个读查询若 1200ms 内未返回，会自动补发同一条查询帧一次。
   - 补发仅限普通 BMS 读寄存器 `0x03` 和 4G 模块专用 `SOCKET_READ=0x0F` 查询帧，用于唤醒 30 秒无通讯后休眠的 BMS 板。
   - 写入命令、BOOT OTA `0x50~0x54`、BLE transport、occupied 云端只读模式不走该补发逻辑，避免影响参数写入和升级包传输语义。
   - 补发触发时输出 `[socket] wakeup resend query`，便于在 Debug 日志或控制台确认休眠唤醒行为。
3. 收紧 4G BMS OTA 数据包 ACK 超时
   - 将 4G MQTT BMS OTA 的 `0x53` 数据包 ACK 检测超时从 20000ms 调整为 3000ms，适配 BMS 板端 4 秒超时窗口，避免 APP 长时间等待后才重发。
   - `0x50/0x51/0x52/0x54` 阶段超时、快速发送节奏、超时后自适应降速和 BLE/仪表 OTA 参数保持不变。
   - 新增独立 runtime options helper，避免后续在参数页再次硬编码 20 秒数据包 ACK 超时。
4. 增强 QoS1 后 4G BMS OTA 包序号诊断与后端桥接优化
   - 生产日志确认 4G 模块订阅 QoS1 已生效，但现场延迟样例中云端仅收到 `0x04FA` ACK，未收到 `0x04FB` ACK；重复下发的是同一 `0x04FA` 数据包，不是 APP/后端继续推进到下一包。
   - `/api/v1/app/battery/socket/ws` 的 BOOT 结构化日志新增 `boot_packet_seq_hex`、`boot_expected_ack_hex`、`boot_ack_requested_hex`、`boot_ack_for_packet_hex`、`boot_packet_attempt`、`boot_packet_retry_count`、`mqtt_message_id`、`mqtt_publish_message_id` 等字段。
   - APP WebSocket 下行数据包不再每帧强制刷新 Redis owner，改为 5 秒节流刷新，`ping` 仍强制刷新，降低 OTA 高频下发期间 Redis 偶发抖动拖慢桥接链路的风险。
   - `bms_bridge_comm_logs.parsed_summary` 对 BOOT 帧增加包序号摘要，4G 模块上行 ACK 可在生产库中直接看到 `boot_ack_requested_hex` 与对应确认的 `boot_ack_for_packet_hex`。
   - `bms_bridge_comm_logs` 记录 MQTT 上行实际 QoS 与 broker message id，便于继续核对 4G 模块 QoS1 上行是否连续。
5. App Debug OTA 日志补充包序号显示
   - `boot-ota.ts` 的 `[boot] packet timing`、`[boot] packet timeout, retry`、`[boot] packet ack` 等日志增加 `packetIndexHex`、`expectedAckHex`、`requestedHex`、`ackForPacketHex`。
   - `UniMqttSocketBmsTransport` 的 `[socket] boot request timing` 请求与响应摘要同步增加 16 位 BOOT 包序号和 ACK 序号字段。
   - Debug 模式 OTA 日志浮层不改 UI 结构，继续复用现有日志数据展示和复制能力；新增字段会随日志 JSON 一起显示和复制。

## 2026-06-29
1. 修复 4G BMS 详情实时数值可能不刷新的问题
   - 生产视频和 `bms_bridge_comm_logs` 复核显示目标设备在测试期间持续上报，数据库当前遥测已变化，但移动端实时轮询可能继续保留旧 `status`。
   - `UniMqttSocketBmsTransport` 对普通 `0x03` 读寄存器响应增加期望字节数匹配，避免同一 Socket 中迟到的短响应误唤醒当前大范围状态读取。
   - `BmsClient.readRegisters()` 增加返回寄存器数量校验；普通 `0x03` 响应必须等于本次请求数量，`SOCKET_READ=0x0F` 响应仍允许覆盖更大地址范围但校验 payload 数量与响应头一致。
   - UniApp 4G/MQTT 实时轮询失败时立即刷新一次云端当前遥测，使用生产库已入库的主动上报快照替换旧值；下一次实时读取成功后仍切回 `realtime`。
   - 蓝牙 BMS、仪表会话、occupied 云端只读和 OTA BOOT 传输路径保持原行为。

## 2026-07-02
1. 优化移动端 4G BMS 高级参数读取体验
   - 生产 MQTT 直连确认目标设备高级参数普通 `0x03` 读寄存器可在 1~3 秒内返回，慢加载主要来自移动端串行队列被前置状态/超时请求占住。
   - `BmsClient.readAllStatus()` 增加 `shouldContinue` 检查点；设备详情进入设置页暂停轮询后，旧状态读取不会继续排后续状态子请求，减少高级参数排队等待。
   - 轮询取消视为预期状态，不触发首帧失败、蓝牙仪表透传失败计数或 4G 云端兜底刷新。
   - `readParamsByKeys()` 支持传入 `timeoutMs`，UniApp 在 `connType=mqtt` 参数读取时使用 5 秒单组超时，避免个别无响应区间按默认 10 秒持续拖慢后续分组。
   - 暂不做 transport 级强制取消 in-flight 请求，避免普通 `0x03` 单寄存器迟到响应污染后续同字节数参数请求。

## 2026-07-03
1. 按 4G BMS 三分钟休眠策略优化参数读取前唤醒
   - 根据设备端确认：4G BMS 在无 MQTT 通讯且无串口通讯约 3 分钟后进入休眠，休眠状态首个下行读指令可能只用于唤醒而不响应。
   - `UniMqttSocketBmsTransport` 默认休眠判断阈值从 30 秒调整为 180 秒，并暴露 `shouldRunSleepWakeupProbe()`，用于页面在进入参数读取前判断是否需要主动唤醒探测。
   - `BmsClient` 新增 `wakeupReadLink()`，默认发送轻量 `0x0100 qty=1` 读查询，可设置短超时；探测失败只记录调试日志并返回 `false`，不会阻断后续真实参数读取。
   - UniApp 参数页在首次展开基础分组、打开“高级参数”弹层前，若当前为 MQTT 实时连接且可能已休眠，会先执行 2.5 秒短超时唤醒探测；探测成功或超时后都继续读取真实参数。
   - 高级参数弹层增加加载序号保护，用户关闭或切换连接后，旧的异步唤醒/加载任务不会继续触发参数读取。

## 2026-07-07
1. 修复 4G BMS 小程序实时回包与仪表盘轮询链路
   - `UniMqttSocketBmsTransport.onMessage()` 改为统一解码 `string`、`ArrayBuffer`、`TypedArray` 和数组消息，避免微信小程序 WebSocket 回包被转成 `"[object ArrayBuffer]"` 后误判为桥接错误并关闭连接。
   - MQTT Socket 收包在没有 `hex` 时仅对明确桥接错误文本或 `socket_error/socket_occupied` 控制消息 reject pending；未知非帧消息记录调试日志后忽略，避免 `pong`、平台包装对象或其它控制文本污染当前实时读请求。
   - 设备详情在仪表盘/电芯页增加连接就绪 watcher：用户停留在仪表盘时，只要 4G MQTT client 后续创建成功，会主动 `resumePolling()`，确保持续下发 `readAllStatus()` 读取请求。
   - `useBatteryDetail.startPolling()` 增加当前 client 与 generation 保护，同一实时连接已在轮询时不重复启动；切到参数页、断开连接或换连接后，旧轮询不会继续排下一轮，也不会用迟到状态覆盖当前页面。
   - 4G MQTT 状态轮询将 `readAllStatus()` 单段读取超时下调为 5 秒，并把 `timeoutMs` 贯通到 `readSn/head/alarm/tail` 子读取，避免单段无响应把仪表盘轮询和参数读取队列拖住过久。
   - 后端 `/api/v1/app/battery/socket/ws` 对普通非 BOOT 帧补充 `ws_to_mqtt_rx` 与 `mqtt_tx_to_ws` 结构化日志，包含 topic、payload 摘要、frame source/target/function、publish/write 耗时和失败原因；普通帧 WebSocket 写失败不再静默。
2. 修复 4G BMS 参数设置“单体设置”回包已到但小程序不展开
   - 现场 MQTTX 确认 `0x040D qty=4` 请求 `7F55FE0103040D0004D4FAFD` 可在约 150ms 内收到普通 `0x03` 回包 `7F5501FE030814140B5409603214D464FD`，协议匹配层可正常识别，问题不在设备端回包。
   - 移动端单体设置参数清单漏掉 `LOW_TEMP_CELL_UV_ALARM_V` 与 `LOW_TEMP_CELL_UV_PROTECT_V`，导致 `0x0408~0x0410` 连续配置区被拆成 `0x0408 qty=3` 和 `0x040D qty=4` 两段；补齐后单体欠压相关配置合并为 `0x0408 qty=9` 一次读取，减少 4G 透传请求数并避免后段单独请求卡住界面。
   - 参数分组加载在 MQTT 模式下若首次读取没有任何有效值，会短间隔重试一次；重试后仍全空则返回失败并保持分组未加载，不再把失败结果吞掉后让用户停留在持续转圈或空值状态。
   - 基础分组展开逻辑会根据 `loadSection()` 返回值决定是否展开，读取失败时 toast 提示并保留可再次点击重试的状态。
3. 根据 MQTTX 导出日志修正参数读取超时
   - `_resources/fjia.json` 显示单体设置的 `0x0408 qty=9` 曾在 `2026-07-07 11:15:22.268` 下发并于 `11:15:22.440` 快速返回，也曾在 `11:15:32.425/11:15:33.645` 下发后到 `11:15:35.803` 才收到回包；真实设备同一参数区间存在秒级波动。
   - 之前将 MQTT 参数读取单组超时压到 5 秒，用于避免高级参数被前置状态请求拖慢；但在本设备慢回包窗口下会把仍会返回的参数读取判为失败，触发“打开失败，请重试”。
   - UniApp MQTT 参数分组读取超时调整为 15 秒，仍保留进入参数页暂停实时轮询、休眠唤醒 probe、全空重试和失败不缓存的策略，避免恢复到约 1 分钟 fallback 等待。
   - 补充完整 Transport 断言：当 WebSocket 收到 `0x0408 qty=9` 有效帧后拼接尾随字节时，`FrameCollector` 仍应切出有效帧并返回 9 个寄存器，覆盖 MQTTX 中 `...66F0FD150C...` 这类 payload。
4. 修复 MQTT Socket 帧收集器被下行请求帧卡住的问题
   - `_resources/fjia2.json` 前段显示小程序下发 `0x0100 qty=1`、`0x0400 qty=6`、`0x0408 qty=9` 后设备均有普通 `0x03` 响应；若 WebSocket 流中先混入同一条下行请求帧，旧 `FrameCollector` 会反复从错误起点解析失败，后续真实响应被留在缓冲区，最终 pending 超时并提示“打开失败，请重试”。
   - `FrameCollector.tryShiftOneValidFrame()` 改为按响应功能码计算期望帧长，遇到请求帧、未知功能码、错误帧尾或 CRC 不匹配时丢弃当前错误起点后继续扫描；有效响应帧后仍保留尾随字节供下一次解析。
   - 新增 `uni-mqtt-socket-transport-fjia2-repro.test.ts`，使用 `fjia2.json` 中的真实响应帧，并在每条响应前注入请求 echo，确认 4G BMS 单体参数分组仍可展开并解码出参数值。
5. 调整 4G 设备数据交互置在线逻辑
   - 后端 `/api/v1/app/battery/socket/ws` 在订阅到 `device/socket/tx/{device_number}` 非 retained 上行回包后，异步调用 4G 设备交互置在线逻辑；仅对 `bms_comm_type=2/3` 或存在 `comm_chip_id` 的设备生效。
   - 在线状态刷新以设备侧回包为依据，不因 APP 下发请求、Socket 建连或 ping 直接置在线；刷新 `devices.is_online=1` 后同步发布设备状态消息，并用 `heartbeat.default_online_ttl_sec` 刷新在线 TTL。
   - WebSocket 上行回包置在线按会话 30 秒节流，避免详情页实时轮询时每帧触发数据库更新。
   - UniApp 详情页在 MQTT `readAllStatus()` 成功后同步将当前 `battery.is_online` 置为 `1`，让顶部 4G 状态与已经刷新的仪表盘数据保持一致。

## 2026-07-10
1. 增加移动端详情数据源仲裁
   - 新增独立 `detail-data-arbiter`，每次设备详情/仪表会话加载生成 session generation，设备详情、云端遥测、连接、轮询、重连和页面卸载统一校验会话有效性。
   - 云端请求记录 request sequence、发起时的 realtime success sequence、响应 `device_id` 与 `last_report_ts` 水位；旧请求、跨设备响应、实时恢复后的迟到响应和时间倒退响应均不再写入当前页面。fallback 的云端时间若早于最后实时成功时间超过 5 秒，也只保留 last-good 实时状态。
   - 已成功展示实时帧后，单次 MQTT 状态读取失败继续保留最后实时数据；只有连续失败至少 2 次且最后实时成功已超过 10 秒，才允许使用云端当前遥测兜底。
   - 首帧尚未返回时仍允许云端快照快速填充；实时帧一旦成功，正在途中的 bootstrap/fallback 响应立即失效。
   - `cloud_mode` 仅在无实时 client 时运行；fallback 绑定 polling generation 与原 client，切入参数/历史页或连接变化后不提交，也不把存活的 MQTT client 改成 offline。
   - 页面卸载增加永久 disposed latch，扫码、仪表延迟重连、延迟恢复轮询和 relay 参数命令均增加页面/session/task/client 校验，旧异步任务不能重新连接或跨设备执行。
2. 加固 MQTT 上行新鲜度与处理顺序
   - APP Socket WebSocket 和 bms-bridge 对所有 retained 上行帧直接丢弃，避免历史状态帧或 BOOT ACK 参与当前会话。
   - bms-bridge 单独启用 clean session、关闭离线订阅恢复并启用有序回调；主 MQTT adapter 保持历史默认配置。
   - bms-bridge 按原始 Topic 设备标识哈希分片，同一设备固定进入同一 FIFO worker，跨设备仍可并行处理；同设备接收时间生成严格递增毫秒，避免同毫秒帧结果依批次边界变化。
3. 保留原始采集时间并阻止当前值倒退
   - bms-bridge 发布结构化遥测时增加 `source=bms_bridge` 与桥接接收时间戳；MQTT adapter 拒绝超过接收时间 5 分钟的未来值，uplink 仅对 bridge metadata 保留该时间，普通设备继续使用原 storage 处理时刻。
   - bridge uplink 到 storage 不再二次覆盖消息时间；`telemetry_current_datas` 的批量和逐条 upsert 仅接受时间不早于当前行的数据。
   - 修复逐条 fallback 在同一 key 对应多条历史记录时按数组下标取 current 可能越界或错配的问题，改为按 `device_id + key` 映射。
   - 当前遥测接口增加 `snapshot_ts`；后端只允许不早于快照的逐 key current 覆盖快照，移动端仅在 `snapshot_ts >= last_report_ts` 时整体采用快照，否则使用逐 key current 合成仪表盘和电芯状态。
4. 兼容性控制
   - BLE-only、仪表会话、参数读取、OTA、Socket owner 互斥和主 MQTT adapter 默认会话参数不变。
   - 本次不新增数据库表或字段，后端各防线和移动端仲裁可独立回滚。

## 2026-07-20
1. 参数设置页与历史记录页增加 4G BMS 低频保活轮询
   - 根据设备端约 3 分钟无 MQTT/串口通讯进入休眠的策略，将 4G MQTT 参数设置页和历史记录页从完全暂停状态轮询调整为每 30 秒执行一次 `readAllStatus()`，持续产生真实设备通讯并刷新交互在线状态。
   - 新增详情 Tab 轮询策略：仪表盘/电芯页保持默认 2 秒轮询，4G MQTT 参数页和历史记录页使用 30 秒低频轮询，对应 BLE Tab 继续暂停。
   - 参数/历史页首轮低频状态读取延后 30 秒，避免刚切入 Tab 时抢占自动 `FUNCTION_CONFIG`、参数分组或历史记录读取；后续状态读取仍通过 `UniMqttSocketBmsTransport` 串行队列发送，不与业务读取并发。
   - `useBatteryDetail.startPolling()` 支持独立配置轮询间隔和首轮延时；切换策略时沿用 polling generation，使旧轮询不能继续排后续状态子请求或覆盖当前状态。
   - 参数弹层、参数编辑结束和 OTA 结束后的轮询恢复统一回到当前 Tab 策略；OTA 执行期间仍显式暂停轮询，完成后恢复 30 秒保活。历史页切换保护次数/状态记录或加载更多时不重置保活周期。
2. 兼容性控制
   - 本次只改变 `connType=mqtt` 的参数设置页和历史记录页；BLE-only、仪表会话、Web 后台和后端接口保持原行为。
   - 新增纯函数策略断言，覆盖仪表盘正常轮询、4G 参数/历史页 30 秒保活、BLE 参数/历史页暂停和连接未就绪暂停。
3. 修复 Web 端 `0xFFFF` 电芯电压误显示
   - 根因是 Web BMS 面板对实时/云端电芯数组只做有限数校验，随后无条件除以 `1000`；`65535 mV` 因而被显示为 `65.535 V`。
   - `displayStatus.cell.voltagesMv` 的非空数组始终优先于云端数组，导致全 `65535` 的实时占位数组还会遮蔽有效的云端电芯数据。
   - 新增 `selectDisplayCellVoltagesMv()`：仅接受 `0 < mv < 0xFFFF` 的电芯值，实时数组全无效时回退云端数组，两者均无有效值时展示空态。
   - 部分无效数组使用 `null` 保留原位置，页面将对应电芯显示为 `-`，不参与最高/最低高亮，避免压缩数组造成电芯编号错位。
4. 回归保护
   - 新增 `cell-voltage.test.ts`，覆盖全无效实时数组回退、两侧全无效为空、部分无效保序和数值字符串归一化。

## 2026-07-25
1. 增加 4G APP 主动读取快照
   - UniApp 在当前 MQTT Socket 会话的 `readAllStatus()` 完整成功后，异步提交本次整组 `BmsStatus`；BLE、仪表、参数读取和失败/超时响应不提交。
   - Transport 从后端 `socket_ready` 控制消息保存 `session_id`，断开、错误或主动关闭时立即清空，避免旧会话继续上报。
   - 上报采用单请求泵：同一时刻最多一个 HTTP 请求在途，轮询期间只保留最新待提交快照；失败仅记录日志，不阻塞实时读数和页面渲染。
2. 增加后端会话鉴权和独立存储
   - 新增 `POST /api/v1/app/battery/interactive-snapshot`，先复用 APP 设备可见性和 4G 类型校验，再严格匹配 Redis `bms:mqtt_socket:owner:{device_id}` 中的设备、会话、用户、租户和有效期。
   - 使用后端接收时间将完整快照写入 `telemetry_current_datas` 独立键 `bms.mqtt_interactive_snapshot`，仅维护 current，不写历史表；upsert 只接受不早于现值的时间，防止迟到请求回退快照。
   - `current-telemetry` 返回独立的 `interactive_snapshot` 和 `interactive_snapshot_ts`，不把该整包与普通逐项遥测混合。
3. 调整离线 fallback 数据优先级
   - 移动端云端状态按“APP 主动读取快照 > 有效普通 `bms.snapshot` > 普通 current 合成”选择。
   - 无主动读取快照、旧版本客户端或主动快照接口失败时保持现有普通主动上报 fallback，接口新增字段为可选字段，不影响旧客户端。
4. 数据与发布范围
   - 本次不新增数据库表或字段，不修改主 MQTT 上报链路和历史遥测语义。
   - 功能进入 `review`，待后端发布后使用真实 4G BMS 在微信小程序、iOS、Android 验证在线主动读取、离线 fallback、账号/会话切换和弱网失败行为。

## 2026-08-21
1. 增加扫码进入 4G 详情的 60 秒本地在线宽限
   - 相机扫码直达、UUID 绑定和扫码 BLE 配网链路统一透传 `entry_source=scan`；普通首页/组织设备详情和手动 BLE 搜索保持无标记。
   - 详情基础信息确认设备具备 4G 能力后立即显示“4G 在线”并隐藏连接遮罩，后台继续复用现有串行 `readAllStatus()` 轮询；扫码本身不调用后端在线状态接口。
   - 新增纯函数状态策略，以初始确认时间或最近一次匹配有效回包时间计算 60 秒保护窗口；窗口内完全无有效回包且后端仍离线时才显示“4G 离线”，之后收到有效回包可恢复。
2. 将在线确认收敛到 MQTT 当前请求的有效回包
   - `UniMqttSocketBmsTransportOptions` 增加可选匹配响应回调，仅在 `_handleFrame()` 校验通过后触发；`socket_ready`、心跳、错误文本、非法帧和意外帧均不计为成功。
   - 回调绑定当前 Transport、设备 ID 和详情 session generation；切换设备、页面卸载或旧 Transport 迟到时不更新当前页面，并清理宽限定时器。
3. 保持兼容边界
   - 不修改后端 API、数据库、MQTT Topic 或在线 TTL；BLE-only 和普通详情入口不启用宽限。
4. 根据现场 15 秒休眠阈值加密参数页保活
   - 现场确认 4G 板在参数设置页约 15 秒没有数据交互就会进入休眠，原参数页 30 秒保活无法覆盖该阈值；将 4G MQTT 参数页首轮读取和后续间隔均调整为 10 秒，预留约 5 秒链路裕量。
   - 历史记录页仍维持 30 秒首轮延时与 30 秒间隔，本次不扩大到历史业务命令链路；BLE 参数页和历史页继续暂停状态轮询。
   - 继续复用详情页单一 `readAllStatus()` 轮询生命周期、polling generation 和 Transport 串行队列，不增加第二个定时读取线程；参数展开、读取、写入或 OTA 占用队列时，状态保活只能串行等待。
   - 更新 `detail-polling-policy.test.ts`，覆盖参数页 10 秒首轮/间隔且小于 15 秒阈值、历史页仍为 30 秒、BLE 与未连接状态继续暂停。

## 2026-08-28
1. 按客户验证方案调整移动端 OTA 非完成帧应答窗口
   - 将共享 `MOBILE_BOOT_NON_FINALIZE_TIMEOUT_MS` 从450ms调整为900ms，BLE与4G/MQTT的 `0x50`～`0x53` 同步生效。
   - 保留 `0x53` 超时后220ms重发缓冲、ACK后主动等待预算、BLE `0x54` 800ms间隔最多8次，以及MQTT/4G `0x54` 单发5秒策略。
   - 更新运行参数断言并保留Boot时序模拟，真实微信小程序、Android、iOS及4G设备成功率待客户验证。

## 2026-08-30
1. 修复底部加号扫码配网后的 4G 在线宽限遗漏
   - 根因是配网成功产生 `DeviceDetailHandoff` 后，详情 `loadById()` 进入暖连接快速分支并提前返回，原 60 秒宽限只写在普通云端详情分支，因此扫码来源即使已透传也不会启动宽限。
   - handoff 新增一次性 `entrySource=scan`，扫码配网页保存该来源；详情以显式 `entry_source=scan` 或 handoff 来源任一命中作为扫码会话，消费后不会污染首页或手动搜索的后续详情。
   - 将宽限启动收敛为同一幂等入口，普通详情与 handoff 分支均调用；handoff 已确认 4G 时立即启动，交接数据不足时在详情接口补全后补启动，同一 session 不重复重置 60 秒起点。
2. 保持既有连接与在线边界
   - 不改变暖 BLE 复用、MQTT 建连、串行 `readAllStatus()`、后端 `is_online`、在线 TTL、参数轮询或 OTA 逻辑。
   - 匹配当前 MQTT 请求的有效回包仍按原策略刷新 60 秒保护；普通入口、BLE-only 和手动 BLE 搜索不启用。

## 2026-09-02
1. 按客户新一轮验证方案调整移动端 OTA 非完成帧应答窗口
   - 将共享 `MOBILE_BOOT_NON_FINALIZE_TIMEOUT_MS` 从900ms调整为600ms，BLE与4G/MQTT的 `0x50`～`0x53` 同步生效。
   - 保留 `0x53` 超时后220ms重发缓冲、ACK后主动等待预算及既有 `0x54` 完成策略，待真机继续验证。
2. 按最终确认恢复700ms以内重发节拍
   - 将共享 `MOBILE_BOOT_NON_FINALIZE_TIMEOUT_MS` 从600ms恢复为450ms，继续保留220ms重发等待，BLE与4G/MQTT总节拍均为670ms。
   - MQTT/4G的40ms最小帧间隔、自适应降速、页边界等待与单发5秒 `0x54` 策略不变，保留一次真机冒烟回归门槛。
3. 将首页设备列表纳入 4G 在线宽限
   - 首页设备卡片进入详情时增加 `entry_source=home`；详情来源策略仅将 `scan` 与 `home` 映射到既有 60 秒在线宽限，组织设备列表和手动 BLE 搜索保持原行为。
   - 复用原 `loadById()`、串行 `readAllStatus()`、匹配有效回包续期及 session 清理逻辑，不新增轮询、定时器类型或后端状态写入。

## 2026-09-03

1. 修复BLE与4G共用的OTA状态机
   - 对照旧版 `_resources/vendor.js`，将 `0x53` 的220ms重发等待改为持续可接收ACK的窗口，450ms后不销毁pending，满670ms无ACK才重发；共享引擎不再叠加第二次220ms等待。
   - 成功ACK必须匹配当前期望 `requested`；忽略旧/未来成功ACK，显式回退与重新准备有恢复上限，避免重复成功ACK回退和重置预算。保持设备指定包长及真实 `0x54 status=0` 完成条件。
2. 修复4G OTA被普通状态轮询插队
   - 详情页 `otaRunning` 对所有会话生效，避免cloud会话watch重新启动参数页10秒轮询；MQTT增加与BLE一致的Boot独占，取消在途/排队普通请求与唤醒补发，OTA结束后恢复普通读取。
   - Socket心跳、服务端owner互斥和保留消息过滤不变，不新增后端API或队列。Boot接收器跨通知持续组帧，坏帧/普通帧不吞掉后续有效ACK；修正纯hex消息被成功识别后仍提前return的问题。
3. 本地回归与验收边界
   - 实际BLE/MQTT传输代码的模拟测试覆盖449/500/669ms ACK与约670ms重发；时序、运行参数、普通响应匹配、休眠唤醒、fjia2真实样例、页面watch与独占恢复、SFC和类型检查均通过，详见测试报告。
   - 本轮只修改移动端与文档，保留首页/扫码在线宽限的既有改动，未提交、推送或部署。Android微信小程序/App的4G连续升级、弱网与版本变化未真机验收，状态回到 `in_progress`；不能据模拟结果宣称100%成功。

## 2026-09-03 客户超时推进试验

1. 根据客户最新明确要求，替代前轮同包重发方案：450ms+220ms无ACK后推进下一包，首包、中途、末包一致；设备明确要求旧包时有界补发，请求当前下一包时继续。断连、取消与真实写失败不被当作ACK超时吞掉。
2. 对齐旧版数据节奏：`0x52` ACK后立即首发，MQTT OTA期间最小帧间隔、包间/4KB等待设0，移除超时降速；结束恢复普通通讯间隔。数据尝试发送完后继续最终CRC32校验，仍需真实 `0x54 status=0`，保留300ms收尾等待与单发5秒窗口。
3. 共用OTA日志改为Boot期间有界内存追加、结束统一发布/保存；实时复制读取内存，避免逐条同步全量落盘和列表重建拖慢ACK流程。未新增后端接口、依赖或日志上传。
4. 13项本地回归、TypeScript和SFC编译通过；真实MQTT transport接模拟Socket验证首/中/末包超时670～672ms后继续，数据真丢失时按设备请求补包，全无数据ACK也必须实际最终确认，最终拒绝/无应答均失败。该结果仅对应当时试验，完整清单见FEAT-0046测试报告历史试验节。
5. 超时推进不是已从旧源码证实的原有行为，真实蜂窝丢包仍可能最终失败；Android小程序/App连续升级、弱网与版本变化，以及iOS冒烟仍待验收。未提交、推送、打包或发布，文档看板保持 `in_progress`。

## 2026-09-04 共享OTA状态机最终收敛

1. 根据BLE失败日志在4KB页首包形成序号空洞的证据，撤销9月3日“670ms无ACK继续下一包”和“末包缺ACK仍进入完成阶段”试验；该结论同步适用于经MQTT Socket透传的4G BMS OTA，不能假设Broker已接收就等于Bootloader已写入。
2. 4G/MQTT `0x53` 保持450ms主窗口和220ms连续宽限，满670ms仍无ACK时重发同一包；设备应答中的合法 `requested` 成为唯一发送游标，主机不再自行递增。`status=3` 可按设备游标确认前进或有界回退，只有新的确认高水位才重置恢复预算。
3. BLE与MQTT/4G数据阶段均设置 `minFrameIntervalMs=0`、`packetDelayMs=0`，普通包无额外固定等待；两类链路共用300ms的4KB页边界保护：确认一整页后再等待，随后发送下一页首包；同一页首包超时重试不重复等待，设备回退后重新跨越边界时再次保护。OTA期间的队列独占、普通轮询暂停和WebSocket ping保持原设计。
4. 全部数据必须确认到 `requested == packetTotal` 后才发送真实CRC32的 `0x54`；4G/MQTT仍为单发5秒严格窗口，只接受真实 `0x54 status=0`，不采用BLE完成后断连兼容。
5. 共用OTA日志采用有界内存和延迟落盘；每个 `0x53` 数据包保留一条包含 `seq/status/requested/RTT` 的紧凑结构化 ACK，删除 Boot 层重复的 `0x53` 完整十六进制记录，完整十六进制只保留首包、末包、4KB边界包、同包重试和异常；不修改后端桥接日志、接口、数据库、Topic、owner或依赖。
6. 9月3日试验记录保留为失败历史，本节为现行方案。Android微信小程序/App真实4G升级各20次、至少一次弱网、升级后版本变化、iOS冒烟及MQTTX/后端链路核对未完成，状态保持 `in_progress`。
7. 本地回归已通过共享Boot时序/运行参数、BLE/MQTT实际transport、普通MQTT响应/wakeup/fjia2、OTA页面会话、轮询策略、日志精简、TypeScript及详情/参数SFC编译；这些静态与模拟结果不替代真机4G验收。

## 2026-09-04 Android BLE后续修复边界

1. 最新Android日志后续修复只调整BLE特征写能力、原生写回调和通知读取探测；未修改共享Boot状态机、`UniMqttSocketBmsTransport`、后端桥接、数据库、Topic、owner或依赖。
2. 4G/MQTT继续使用450ms+220ms连续ACK窗口、670ms同包重发、300ms页保护、数据完整确认、单发5秒 `0x54 status=0` 与OTA独占；不引入Android原生写回调或BLE读取探测。
3. 本轮仅补MQTT transport与共享运行参数回归；Android微信小程序/App的4G各20次、弱网、版本变化和iOS冒烟仍待真机，状态保持 `in_progress`。
