# FEAT-0071 第三方 MES 批量重新分配 PACK 厂 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-07-28
- related_feature: FEAT-0071
- version: v0.2.0

## 1. 测试范围

- MES OpenAPI 请求校验、租户隔离和目标 PACK 解析。
- 批量部分成功、设备资格校验、幂等、事务和审计。
- Swagger、接入文档与联调脚本。

## 2. 自动化结果

### 2.1 定向 Go 测试

命令：

```bash
cd backend
go test ./internal/api ./internal/service \
  -run 'TestMESPackFactoryReassignRequestBinding|TestNormalizeMESPackFactoryReassignSerials|TestResolveMESReassignTargetPackFactory|TestReassignPackFactoryForMES' \
  -count=1
```

结果：通过。

覆盖：

- 缺少/空 SN、重复 SN、大小写敏感、空项、超过 500 条和缺少目标 PACK。
- 目标 PACK 不存在、类型错误、禁用、重名和跨租户。
- 合法转移、`pack_factory_org_id` 为空时按当前 PACK 补全、部分成功、全部设备级失败语义和结果顺序。
- 未出厂、当前持有方非 PACK、已激活/异常激活状态、所有者绑定、后续流转、PACK 信息已补全、两个 PACK 字段不一致、跨租户和不存在。
- 目标已一致时 `UNCHANGED`，不增加转移日志。
- 两个 PACK 字段同时更新、来源 PACK 名称回显、操作日志元数据和审计失败整台回滚。

### 2.2 并发与 race

命令：

```bash
cd backend
go test -race ./internal/service \
  -run 'TestReassignPackFactoryForMESConcurrentRetryCreatesOneTransfer|TestReassignPackFactoryForMESPartialSuccessAndEligibility|TestReassignPackFactoryForMESRollsBackWhenAuditFails' \
  -count=1
```

结果：通过；并发重复请求仅产生一次实际转移，另一请求返回 `UNCHANGED`。

### 2.3 Swagger 与联调脚本

命令：

```bash
cd backend
swag init
python3 -m py_compile docs/scripts/test_openapi_mes_battery.py
python3 docs/scripts/test_openapi_mes_battery.py --help
```

结果：通过；生成文件包含新路径与请求/响应模型。当前仓库 Swagger 基线自 2025-12-26 后未同步，标准重新生成同时纳入了现有源码中其他已存在接口，因此生成文件差异较大。

### 2.4 全量 Go 测试

命令：

```bash
cd backend
go test ./...
```

结果：FEAT-0071 所在 `internal/api`、`internal/service` 及其他大部分包通过；全量命令退出码为 1，失败来自两个既有环境型测试：

- `project/initialize/test.TestSetDevice`：测试未初始化告警缓存依赖，在 `initialize/alarm_cache.go:105` 空指针 panic。
- `project/test.TestDatebase`：未提供 `run_env`，先报“未知环境”，随后对空 GORM DB 执行 SQL 导致 panic。

上述失败与本功能代码路径无关，本次未修改这两个测试或其环境依赖。

### 2.5 差异检查

- `backend` 与项目根目录 `git diff --check`：通过。
- 接入指南明文样式 `app_*`/`sk_*` 长密钥扫描：通过，当前文档仅保留占位符。

## 3. 待现场验收

- 测试环境 MES 密钥联调。
- 真实未投入使用 BMS 板从原 PACK 迁移至目标 PACK。
- 混合失败、超时重试后 `UNCHANGED`、查询接口回显新持有方和跨租户拒绝。
- 测试环境联调未执行前，功能状态保持 `review`，不标记 `done`。
