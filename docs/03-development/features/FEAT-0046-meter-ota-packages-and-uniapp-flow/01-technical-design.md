# FEAT-0046 仪表 OTA 升级包与 UniApp 独立升级链路 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-09-02
- related_feature: FEAT-0046
- version: v0.1.2

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
  - BLE 连接阶段必须有超时出口：同一 MAC 的 `inFlight` 任务与连接串行队列等待上一任务超过 8s 后允许新任务继续；详情页主动取消旧连接后，新连接只保留短等待窗口，避免旧连接锁拖慢仪表详情首连；`createBLEConnection` 不允许无限等待，Android 使用 6.5s 超时，iOS 使用 9s 超时。
  - 确认升级后直接下载 `package_url` 并调用 `bootOtaUpgrade()`；升级写包目标地址固定为 `0xFC`。
  - 依据真实仪表升级日志与蓝牙链路约束，Boot 查询 `0x50` 使用广播目标地址 `0x00`，不发送 `0x51` 进入 Boot；蓝牙仪表升级时 `0x52` 的第二段 4 字节参数固定为 `9600`。
  - BLE/MQTT 透传层对 Boot 应答做地址兼容：仪表 OTA 虽然下发目标地址为 `0xFC`，但设备回包源地址仍可能为 BMS Bootloader 地址 `0x01`，transport 必须接受该特例。
  - iOS 末段写包超时后，BLE transport 必须清理超时残留 pending 再进行 0x53 重试；`0x53` 回包 `status=5` 按“固件包大小与设备不一致”展示。
  - 全部移动端 OTA 的 `0x50`～`0x53` 单次应答超时统一为 600ms，超时后的 `0x53` 重发保留 220ms 缓冲；蓝牙非 `0x54` Boot 请求禁用 iOS 替代写二次重试，并将 BLE 写 API 软等待限制为 300ms。该策略取代历史仪表 `0x53` 45s 长应答窗口。蓝牙透传模块仍按单次 BLE 写入透传 Boot 帧，不能把单个 `0x53` Boot 帧拆成多个 20 字节 BLE 写入。
  - 蓝牙 BMS 与蓝牙仪表 OTA 共用完成阶段边界策略：所有 `0x53` 数据包必须 ACK 到 `requested == packetTotal`，等待 300ms 后发送首个 `0x54`；等待应答期间按 800ms 间隔补发，总发送时刻为 `0/800/1600/2400/3200/4000/4800/5600ms`，包含首发共 8 次。
  - 仪表 Android `0x53` 传输阶段继续采用 ACK 驱动和 100ms 最小帧间隔；包间等待与 4KB 边界等待按同一 ACK 后预算合并限制为最多 600ms，历史 1500ms 自适应边界配置会被防御性截断，给 700ms 硬件上限预留调度余量。
  - BLE OTA 在进入 Boot 流程前开启独占通讯会话：取消正在等待的普通状态读取，最多等待 1.2s 清空既有串行队列；升级期间拒绝新的非 Boot 请求，结束后恢复普通轮询，避免 `0x50` 被旧状态请求阻塞约 11s。该队列隔离同时作用于蓝牙 BMS 与蓝牙仪表。
  - 蓝牙 BMS 与蓝牙仪表的 `0x54` 使用单个 6400ms 严格应答窗口，不再启动额外 finalize 轮次或 iOS 替代写模式重试，也不接受残留 `0x53` ACK 作为完成应答。匹配的 `status=0` 应答会立即取消剩余补发并成功；非零状态会立即取消补发并按设备拒绝失败。
  - 全部移动端 OTA 收到有效 `0x52` 应答后固定等待 300ms 再发送首个 `0x53`；重新初始化补发 `0x52` 时应用相同时序。最后一个 `0x53` ACK 后固定等待 300ms 发送首个 `0x54`。MQTT/4G 不使用 BLE 补发策略，仍为单次发送和 5s 严格应答窗口。
  - 仪表 OTA 在上述通用蓝牙边界策略外，继续保留专用协议与时序：`0x50` 广播查询、跳过 `0x51`、`0x52` 固定 9600，以及 Android 仪表专用 ACK 驱动和超时降速保护；BMS OTA 不使用这些仪表专用时序。
  - 开发者模式下，仪表升级卡片下方显示“升级调试日志”：端上记录选包、固件下载、`0x50/0x52` 前置、首包预览、关键 ACK、失败错误对象与成功收敛证据；支持复制与清空，仅做本地展示，不上传后端，不改变升级协议。
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
- 手工验证：
  - 后台双 TAB 查询/新增/编辑/删除
  - BMS 批量 OTA 页面仍只看到 BMS 包
  - 蓝牙仪表详情页选包、确认、升级进度与失败提示
  - 仪表透传 BMS 卡片可见/禁用状态、UUID成功与型号降级、目标 `0x01` 首帧、失败恢复和三条 OTA 链路回归
