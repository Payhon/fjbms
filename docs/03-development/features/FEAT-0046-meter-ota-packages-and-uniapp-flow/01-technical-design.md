# FEAT-0046 仪表 OTA 升级包与 UniApp 独立升级链路 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-26
- related_feature: FEAT-0046
- version: v0.1.0

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
  - 蓝牙已连接但未建立 BMS 透传时，`readAllStatus()` 连续超时达到阈值后停止状态轮询，视为正常空态；保留 `client` 与蓝牙连接，不阻断仪表升级入口。
  - Android 扫描进入仪表详情时同时携带扫描得到的 BLE `deviceId`；连接层优先使用该候选，并过滤与目标 AA MAC 不兼容的 MAC 型候选，防止历史 AC 设备任务串入仪表会话。iOS 扫描得到的 UUID 型 `deviceId` 不参与 MAC 字符串兼容过滤，允许作为直连候选使用。
  - 蓝牙扫描页使用扫描会话 ID 隔离过期回调；停止扫描时立即关闭设备发现监听和 UI 动画状态，扫描时长超时后自动停止并恢复“开始扫描”按钮。
  - BLE 连接阶段必须有超时出口：同一 MAC 的 `inFlight` 任务与连接串行队列等待上一任务超过 8s 后允许新任务继续；详情页主动取消旧连接后，新连接只保留短等待窗口，避免旧连接锁拖慢仪表详情首连；`createBLEConnection` 不允许无限等待，Android 使用 6.5s 超时，iOS 使用 9s 超时。
  - 确认升级后直接下载 `package_url` 并调用 `bootOtaUpgrade()`；升级写包目标地址固定为 `0xFC`。
  - 依据真实仪表升级日志与蓝牙链路约束，Boot 查询 `0x50` 使用广播目标地址 `0x00`，不发送 `0x51` 进入 Boot；蓝牙仪表升级时 `0x52` 的第二段 4 字节参数固定为 `9600`。
  - BLE/MQTT 透传层对 Boot 应答做地址兼容：仪表 OTA 虽然下发目标地址为 `0xFC`，但设备回包源地址仍可能为 BMS Bootloader 地址 `0x01`，transport 必须接受该特例。
  - iOS 末段写包超时后，BLE transport 必须清理超时残留 pending 再进行 0x53 重试；`0x53` 回包 `status=5` 按“固件包大小与设备不一致”展示。
  - 仪表 OTA 的 `0x53` 写包等待时间为 45s，避免 Bootloader 在 4KB/8KB 等页/扇区边界擦写时被 12s 默认超时提前打断；Android 仪表升级额外使用带响应写、最小 220ms 帧间隔、100ms 包间延迟，并在每个 4KB 固件边界写入前等待 1500ms。蓝牙透传模块按单次 BLE 写入透传 Boot 帧，不能把单个 `0x53` Boot 帧拆成多个 20 字节 BLE 写入。
  - 蓝牙 BMS 与蓝牙仪表 OTA 共用完成阶段边界策略：所有 `0x53` 数据包必须 ACK 到 `requested == packetTotal`，再等待固定间隔后发送 `0x54`，并按 300ms/600ms/900ms 额外补发完成指令；BMS 与仪表均必须收到 `0x54 status=0` 才显示成功，不再把 finalize 超时或 BLE 断开收敛为成功。
  - 仪表 Android `0x53` 传输阶段采用 ACK 驱动提速：默认不再对每个 ACK 后增加固定包间等待，最小帧间隔降为 100ms，4KB 边界等待降为 300ms；若出现 `0x53` 超时重试，自动切回慢速保护参数（100ms 包间等待、1500ms 边界等待）。
  - 仪表 OTA 在上述通用蓝牙边界策略外，继续保留专用协议与时序：`0x50` 广播查询、跳过 `0x51`、`0x52` 固定 9600，Android 仪表额外启用带响应写、220ms 最小帧间隔、100ms 包间延迟与 4KB 边界等待；BMS OTA 不使用这些仪表专用时序。
  - 开发者模式下，仪表升级卡片下方显示“升级调试日志”：端上记录选包、固件下载、`0x50/0x52` 前置、首包预览、关键 ACK、失败错误对象与成功收敛证据；支持复制与清空，仅做本地展示，不上传后端，不改变升级协议。
- BMS 设备继续沿用现有 `ota/check -> need_upgrade -> bootOtaUpgrade()` 链路。

## 4. 测试策略
- `cd backend && go test ./internal/service/...`
- `cd frontend && pnpm build`
- `cd fjbms-uniapp && pnpm exec tsc --noEmit`
- 手工验证：
  - 后台双 TAB 查询/新增/编辑/删除
  - BMS 批量 OTA 页面仍只看到 BMS 包
  - 蓝牙仪表详情页选包、确认、升级进度与失败提示
