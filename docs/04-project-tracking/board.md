# 项目进度看板（FJBMS）

> 更新频率：每周例会前至少更新一次；状态变化（进入开发/提测/上线）需当日更新。  
> 状态列与文档生命周期对齐：`draft -> approved -> in_progress -> review -> done -> archived`。

## 看板列定义（统一口径）
- `draft`：需求草拟，尚未评审，至少已有问题背景与目标。
- `approved`：规格评审通过，可进入排期或开发。
- `in_progress`：开发进行中，需持续更新实现日志。
- `review`：代码评审/测试中，等待验收结论。
- `done`：已发布或已交付，文档与看板均已回写。
- `archived`：历史事项归档（通常是完成超过 2 个迭代）。

## 模块泳道看板

### Backend（`backend/`）
- [ ] `in_progress` **FEAT-0007** 蓝牙 BMS 经 App 上云 + 后台 BMS 实时/历史可视化
  - owner：payhon
  - 优先级：P1
  - 依赖：无
  - 文档：`docs/03-development/features/FEAT-0007-bms-ble-cloud-report/`
- [ ] `draft` **FEAT-0004** 电池/MES 对接统一鉴权与审计日志
  - owner：待指派
  - 优先级：P1
  - 依赖：FEAT-0003
  - 文档：`docs/03-development/features/FEAT-0004-mes-auth-audit/`

### Frontend（`frontend/`）
- [ ] `approved` **FEAT-0005** 管理端设备详情页字段对齐（MES 扩展字段）
  - owner：待指派
  - 优先级：P1
  - 依赖：FEAT-0004
  - 文档：`docs/03-development/features/FEAT-0005-admin-device-mes-fields/`

### UniApp（`fjbms-uniapp/`）
- [ ] `in_progress` **FEAT-0006** 升级检测与提示体验优化
  - owner：待指派
  - 优先级：P1
  - 依赖：无
  - 文档：`docs/03-development/features/FEAT-0006-uniapp-upgrade-ux/`

### Docs & Ops（`docs/`, `doc/`, 部署）
- [x] `done` **FEAT-0002** 历史文档迁移与分层重构
  - owner：待指派
  - 优先级：P0
  - 依赖：FEAT-0001
  - 文档：`docs/03-development/features/FEAT-0002-doc-migration/`
- [x] `done` **FEAT-0001** M0 文档治理先行
  - owner：待指派
  - 优先级：P0
  - 依赖：无
  - 文档：`docs/03-development/features/FEAT-0001-m0-documentation-governance/`

## 每周更新模板
- 周期：`YYYY-MM-DD ~ YYYY-MM-DD`
- 新增事项：`N`
- 完成事项：`N`
- 延期事项：`N`
- Top 风险：`...`
- 下周目标：`...`
