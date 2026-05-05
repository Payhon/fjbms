# FEAT-0017 BMS 状态寄存器地址调整、移动端保护状态卡片与旧板兼容读取 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-30
- related_feature: FEAT-0017
- version: v0.1.0

## 1. 测试范围
- 后端 BMS 状态解析编译与扁平化字段输出。
- UniApp 协议类型、参数注册与仪表盘组件类型校验。
- UniApp 仪表盘温度区动态渲染与保护状态卡片默认折叠行为。
- UniApp 蓝牙设备详情状态读取的两段拼装兼容逻辑。
- UniApp 与 Web 端设备详情仪表页顶部故障、告警、保护入口状态源。
- `0x131` 失效状态、`0x134~0x135` 告警状态、`0x12F~0x130` 保护状态的分段解析。
- 协议主文档和看板回写完整性。

## 2. 已执行验证
- [x] `cd backend && go test ./internal/bms/... ./internal/bmsbridge/...`
- [x] `cd frontend && pnpm typecheck`
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`
- [ ] 手工验收：
  - [ ] 电芯温度数量为 `0/1/多路` 时，温度区 `T1/T2...` 序号与行数正确。
  - [ ] `BMS保护状态` 首次进入页面默认收起，点击后可正常展开/收起。
  - [ ] Web 端 BMS 面板保护状态展开/收起与开关文本展示。
  - [ ] 真机或 HBuilderX 查看保护状态卡片展开/收起交互。
  - [ ] 有保护项激活时顶部保护提示与卡片摘要数量一致。
  - [ ] `0x131` 失效状态激活时仅显示故障入口。
  - [ ] `0x134~0x135` 告警状态激活时仅显示告警入口。
  - [ ] `0x12F~0x130` 保护状态激活时仅显示保护入口。
  - [ ] `0x4xx` 配置项开启但只读状态位未触发时，不显示顶部故障/告警/保护入口。
  - [ ] 无保护项激活时卡片仍显示且列表状态为关闭。
  - [ ] 旧款 BMS 板蓝牙设备详情在 `0x135` 或 `0x136~0x140` 不可读时不再失败。
  - [ ] `0x135` 单寄存器读取失败时状态轮询不被中断。

## 3. 当前结论
- `cd backend && go test ./internal/bms/... ./internal/bmsbridge/...`
  - 结果：通过。
  - 备注：编译过程中出现 `gopsutil/disk` 的 macOS 过时 API 警告，不影响测试通过。
- `cd frontend && pnpm typecheck`
  - 结果：通过。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过。
- 协议层兼容性说明：
  - 已将 UniApp 与 Frontend Web `readAllStatus()` 改为 `0x100~0x134`、可选 `0x135`、`0x141~lastAddr` 的兼容读取方式。
  - `0x135` 可读时用于补齐告警状态高 16 位；不可读时按旧板兼容逻辑回填默认值。
  - 后端已补单测覆盖保护状态、失效状态、告警状态三段解析。
  - 旧板兼容仍需通过真机回归确认。
- UI 视觉、旧板兼容性与交互验收待真机验证完成后补充。
