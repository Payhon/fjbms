# 文档工作流（强制）

## 阶段 0：立项（开发前）
1. 创建 `docs/03-development/features/FEAT-xxxx-<slug>/`。
2. 编写 `00-feature-spec.md`（目标、范围、验收标准、风险、回滚方案）。
3. 状态从 `draft` 经评审后改为 `approved`。

## 阶段 1：设计
1. 编写 `01-technical-design.md`（接口、数据结构、异常处理、测试策略）。
2. 关键技术取舍写入 ADR（决策记录）。

## 阶段 2：开发
1. 持续更新 `02-implementation-log.md`（关键决策、偏差、修复）。
2. 每次提交前同步更新看板条目。

## 阶段 3：测试与发布
1. 更新 `03-test-report.md`。
2. 更新 `04-release-note.md`。
3. 看板流转 `In Progress -> Review -> Done`。

## 禁止项
- 无规格文档直接编码
- 开发后不回写文档
- 看板状态与真实进度不一致
