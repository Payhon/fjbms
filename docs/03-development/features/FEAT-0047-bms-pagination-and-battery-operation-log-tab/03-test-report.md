# FEAT-0047 BMS 分页修复与电池详情操作记录 Tab - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-22
- related_feature: FEAT-0047
- version: v0.1.0

## 1. 静态检查与命令
- [x] `cd backend && go test ./internal/service ./internal/api ./router/apps`
- [x] `cd frontend && pnpm typecheck`

## 2. 手工回归场景
### 2.1 分页页回归
- [ ] `BMS管理 > 运营管理 > 操作记录`
  - 总数大于 1 页时，分页显示正确页数。
  - `上一页 / 下一页 / 指定页 / 切换 pageSize` 正常。
- [ ] `BMS管理 > 运营管理 > 激活日志`
  - 同上。
- [ ] `BMS 型号管理`
  - 同上。
- [ ] `API Key 列表`
  - 同上。
- [ ] `APP 用户选择弹窗`
  - 同上。

### 2.2 电池详情操作记录
- [ ] 从 `BMS管理 > 电池列表` 进入 `device_details?bms=1`。
- [ ] 拥有权限时看到 `操作记录` Tab。
- [ ] 选择存在生命周期记录的电池，列表按时间倒序显示。
- [ ] 切换分页与 pageSize 正常。
- [ ] 无权限账号不显示该 Tab。

## 3. 权限矩阵
- `BMS_FACTORY`：应可见（管理员放行）
- `PACK_FACTORY`：默认可见
- `DEALER`：默认可见
- `STORE`：默认不可见

## 4. 结果
- 已完成静态校验：
  - `go test ./internal/service ./internal/api ./router/apps` 通过。
  - `pnpm typecheck` 通过。
- 运行态手工回归尚未在本地浏览器完成，待按分页页与权限矩阵继续验收。
