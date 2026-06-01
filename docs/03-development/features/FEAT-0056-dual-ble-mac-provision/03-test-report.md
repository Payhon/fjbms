# 测试报告

## 自动化

- [x] `cd backend && go test ./internal/service ./internal/bmsbridge`
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
- [x] `cd frontend && pnpm typecheck`

## 覆盖场景

- [x] 外挂蓝牙透传设备连接 MAC 与身份 MAC 不同，允许写入 `identity_ble_mac`。
- [x] 连接 MAC 已属于其他设备时拒绝绑定。
- [x] 已有身份 MAC 与本次读取值不一致时拒绝绑定。
- [x] 旧客户端单 MAC mismatch 仍拒绝绑定。

## 待人工验证

- [ ] 使用生产问题设备实测添加成功。
- [ ] 添加成功后详情页仍使用连接/广播 MAC 自动 BLE 连接。
