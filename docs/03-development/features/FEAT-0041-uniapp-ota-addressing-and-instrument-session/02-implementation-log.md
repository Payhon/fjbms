# FEAT-0041 UniApp OTA 地址口径统一与仪表会话升级支持 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-08-31
- related_feature: FEAT-0041
- version: v0.5.0

## 1. 实施记录
1. 排查 UniApp OTA 入口与 Boot 协议链路，确认当前 Boot 升级主流程已区分仪表/ BMS，但查询地址未严格统一。
2. 确认 OTA 入口在仪表临时会话下被 `allowOta` 直接禁用。
3. 确认后端 OTA 检查接口当前强制要求 `device_id`，导致仪表临时会话无法匹配升级包。
4. 已完成 UniApp OTA 入口调整：
   - `detail.vue` 放开仪表临时会话下 OTA 可用条件
   - 仪表会话也允许自动 OTA 检查
5. 已完成 UniApp OTA 地址口径统一：
   - 仪表 Boot 查询/升级固定 `0xFC`
   - BMS Boot 查询/升级固定 `0x01`
6. 已完成后端 OTA 检查接口兼容：
   - `device_id` 改为可选
   - 无 `device_id` 时按 `model + version` 匹配升级包
7. 已完成定向静态校验：
   - `cd backend && go test ./internal/service/...`
   - `cd fjbms-uniapp && pnpm exec tsc --noEmit`
8. 2026-06-29 补充仪表临时连接浮动提示显隐逻辑：
   - 新增 `meterHasBmsStatus`，在仪表会话下以 `status.value` 是否存在作为已读到下方 BMS 状态的判断。
   - `showMeterScanHandoff` 排除已读到 BMS 状态的有线仪表场景。
   - `showMeterPanelReady` 在首帧读取等待 `bmsDataLoading` 期间不展示提示，避免有线仪表读取成功前短暂误弹。
   - 蓝牙透传型仪表在确认未读到 BMS 状态后仍可展示继续扫码绑定 BMS 的提示。
9. 2026-06-30 补充有线仪表未接 BMS 的失败接管体验：
   - `useBatteryDetail` 返回 `instrumentPassthroughUnavailable`，复用连续 3 次读取失败阈值作为无下方 BMS 状态的判断。
   - `retryBmsDataRead` 与 `reconnectBmsData` 清除仪表无透传状态和失败计数，保证人工重试能重新进入读取流程。
   - `detail.vue` 在 `instrumentPassthroughUnavailable=true` 时允许仪表临时连接浮层显示，同时现有 loading 逻辑关闭，页面回到主面板。
   - 更新中英文浮层提示，统一覆盖有线仪表检查 BMS 板连接/供电和继续扫码绑定 BMS 两类处理方式。
10. 2026-07-25：完成仪表下级 BMS 等待优化：
   - 新增 `INSTRUMENT_PASSTHROUGH_WAIT_TIMEOUT_MS=10_000` 和可测试的等待策略。
   - 仪表蓝牙连接并开始首次状态读取时启动独立截止时间，不再以连续失败次数决定扫码提示时机。
   - 截止时间到期仍无状态时设置 `instrumentPassthroughUnavailable`、停止本轮轮询并关闭 loading，仪表 BLE 连接保持不变。
   - 轮询代次在到期时失效，迟到响应无法回写；读取成功、新会话、断开、销毁、重试和重连均清理旧计时器。
   - 完成 TypeScript、9999/10000ms 策略边界、详情轮询/数据仲裁回归和差异检查。

## 2. 待执行项
- 2026-08-31：微信小程序、iOS、Android 真机复测无 BMS 超过 30 秒后接入、扫码 ACK/超时后无需切页刷新、OTA 与参数/历史页暂停策略。
- 真机验证仪表 / BMS 两类 OTA 行为。
- 真机验证有线仪表已读到 BMS 状态时不展示“仪表临时连接”提示。
- 真机验证有线仪表未接 BMS 时约 10 秒后关闭 loading、回到主面板并显示扫码提示。
- 真机验证蓝牙透传型仪表无 BMS 状态时仍展示扫码提示。

## 3. 当前状态
- 代码修改和静态校验已完成，当前待运行态验收。
- 2026-06-29 仪表提示显隐代码已完成，UniApp TypeScript、代码空白检查、文档/看板空白检查均已通过，待真机回归。
- 2026-06-30 有线仪表未接 BMS 体验代码已完成，UniApp TypeScript、代码空白检查、文档/看板空白检查均已通过，待真机回归。
- 2026-07-25 统一 10 秒等待窗口代码和本地自动化验证已完成，功能进入 `review`；待微信小程序、iOS、Android 真机验证实际时间和临界响应。

## 4. 2026-08-31 持续查询与扫码恢复
- 用户确认保留参数页、历史页的 BLE 轮询暂停，仅仪表盘、电芯页持续等待数据。
- 先更新规格，随后将 10 秒截止改为仅关闭遮罩；沿用 UI 状态字段，但不再终止调度。首帧前轮间等待 1.2 秒，超时后 3 秒，成功后 2 秒，同会话完整迟到响应可更新。
- 新增 `prepareInstrumentBmsSwitch`：有效扫码清除旧数据、首帧状态并使旧轮询失效。非法码、扫码取消保持原数据。
- 重构配置异常处理，仅写配置超时走“结果待确认”，消除 `catch` 中访问作用域外 `parsed` 的错误；不重复写入配置。
- 重连保持 450ms 等待，`loadInstrumentSession` 等待实际连接完成。配置独占期间 watcher 不提前恢复，结束时明确恢复当前 Tab 策略；失败保持离线并提示。
- 页面延迟任务改为可取消、可等待，退出时释放等待 Promise 并阻断旧重连/数据回写；保留原会话、客户端和轮询代次检查。
- 等待 BMS 提示覆盖浮层和收起后的非阻塞提示；补齐中英文等待、配置待确认、重连失败文案。
- 新增生产 composable + 页面 handler 联合模拟测试，覆盖迟到响应、超时恢复、连续切换、重复点击、旧回调、Tab/OTA 和退出边界。TypeScript、SFC、既有策略/协议回归及微信小程序本地编译通过。
- 当前 `review`：未提交、未上传/发布；真机无线仪表与有线仪表验收尚未执行。
