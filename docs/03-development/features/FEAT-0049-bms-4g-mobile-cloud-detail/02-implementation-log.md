# FEAT-0049 BMS 4G 移动端云端详情链路 - 实现日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-30
- related_feature: FEAT-0049
- version: v0.1.0

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
