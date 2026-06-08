# 测试报告

## 自动化

- [x] `cd backend && go test ./internal/service ./internal/bmsbridge`
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
- [x] `cd frontend && pnpm typecheck`
- [x] `cd backend && go test ./internal/service`

## 覆盖场景

- [x] 外挂蓝牙透传设备连接 MAC 与身份 MAC 不同，允许写入 `identity_ble_mac`。
- [x] 连接 MAC 已属于其他设备时拒绝绑定。
- [x] 已有身份 MAC 与本次读取值不一致时拒绝绑定。
- [x] 旧客户端单 MAC mismatch 仍拒绝绑定。
- [x] 终端用户解绑后，无其他终端绑定或机构添加记录时清空 `ble_mac` 并保留 `identity_ble_mac`。
- [x] 终端用户解绑后，仍存在其他终端绑定时不清空 `ble_mac`。
- [x] 终端用户解绑后，仍存在机构添加记录时不清空 `ble_mac`。
- [x] 机构用户移除添加记录后，无其他 APP 侧关联时清空 `ble_mac`。
- [x] 后台强制解绑后，无其他 APP 侧关联时清空 `ble_mac`。
- [x] 协议身份 MAC 未读出时，同一 `item_uuid` 下允许把连接 MAC 从旧外挂模块更新为新外挂模块。
- [x] 协议身份 MAC 未读出时，如果新连接 MAC 已被其他设备占用，绑定仍失败。
- [x] 新连接 MAC 被其他外挂模块历史档案占用时，清空旧档案 `ble_mac` 并让当前 `item_uuid` 接管。
- [x] 新连接 MAC 被其他内置 BLE 身份设备占用时，仍返回冲突错误。
- [x] 同一终端用户重复绑定已绑定设备时返回成功，不新增重复绑定记录。

## 待人工验证

- [ ] 使用生产问题设备实测添加成功。
- [ ] 添加成功后详情页仍使用连接/广播 MAC 自动 BLE 连接。
- [ ] 外挂蓝牙模块 A 解绑 BMS-1 后复用到 BMS-2，确认添加不再被旧 `ble_mac` 占用拦截。
