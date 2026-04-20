# FEAT-0042 电池出厂增强与跨页批量选择 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-04-17
- related_feature: FEAT-0042
- version: v0.1.0

## 1. 自动化校验
- [ ] `cd backend && go test ./...`
- [ ] `cd frontend && pnpm typecheck`

## 2. 手工回归
- [ ] OpenAPI 不传 `pack_factory_name`，建档成功且不触发自动出厂
- [ ] OpenAPI 传唯一匹配的 `pack_factory_name`，建档后自动出厂成功
- [ ] OpenAPI 传不存在/重复的 `pack_factory_name`，建档成功但自动出厂跳过
- [ ] 电池列表跨页勾选后，批量操作数量保持正确
- [ ] 批量出厂全部成功时返回成功汇总
- [ ] 批量出厂部分失败时返回逐台失败明细
- [ ] 更换筛选条件后已选集合清空

## 3. 结果
- 待执行
