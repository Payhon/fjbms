# FEAT-0051 4G模块 OTA 升级包管理 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-05-18
- related_feature: FEAT-0051
- version: v0.1.0

## 测试项
- 后端：`go test ./internal/service ./internal/api -run 'OTA|4G|Version'`
- 前端：`pnpm typecheck`

## 覆盖场景
- `device_kind=3` 解析与校验。
- 4G 模块升级检查缺少租户 ID。
- IMEI 不存在时不升级。
- `imei` 入参命中 `device_batteries.comm_chip_id` 时可正常返回升级包。
- 单个更高版本包直接返回。
- 多个更高版本包无最新标记时不升级。
- 多个更高版本包有最新标记时返回最新包。
- 4G 包创建时同租户 latest 唯一化。

## 结果
- `go test ./internal/service ./internal/api -run 'OTA|4G|Version'`：通过。
- `pnpm typecheck`：通过。
- `go test ./...`：未全量通过，失败点为既有环境型测试：
  - `project/initialize/test`：`TestSetDevice` 在 `AlarmCache.SetDevice` 中 nil pointer panic。
  - `project/test`：`TestDatebase` 因未知环境导致 DB nil pointer panic。

## 2026-05-18 补充验证
- `go test ./internal/service -run 'TestCheck4GModuleUpgrade|TestCreate4GModulePackageLatestUniqueness|TestCompareVersion'`：通过。
