# FEAT-0028 电池调拨路径扩展 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-03-27
- related_feature: FEAT-0028
- version: v0.1.0

## 1. 测试范围
- 后端电池调拨权限矩阵。
- 组织选项接口的上/下级机构返回。
- 管理端电池列表调拨弹窗目标类型展示。

## 2. 测试环境
- 本地开发环境
- 日期：2026-03-27

## 3. 用例结果
- `backend`
  - 命令：`cd backend && go test ./internal/dal ./internal/api ./internal/service`
  - 结果：通过
  - 备注：出现 `github.com/shirou/gopsutil/disk` 的 macOS 弃用告警，不影响本次功能
- `frontend`
  - 命令：`cd frontend && pnpm exec eslint src/views/bms/battery/list/index.vue`
  - 结果：通过
- 手工联调
  - 经销商 -> PACK：待执行
  - 经销商 -> 门店：待执行
  - 门店 -> 经销商：待执行

## 4. 缺陷与风险
- 组织选项接口被多处复用，仍需关注其它页面是否依赖旧的“仅下级”假设。
- 生产环境需用真实组织树样例回归“跨支路调拨仍被拒绝”。

## 5. 结论
- 定向校验已通过，待执行经销商/门店账号的真实组织树联调验收。
