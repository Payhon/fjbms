# FEAT-0045 调拨目标收敛与门店上级组织防泄露 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-21
- related_feature: FEAT-0045
- version: v0.1.0

## 1. 方案概览
- 调拨能力分为两层收口：
  - 前端按账号机构类型收敛调拨目标类型与入口可用性。
  - 后端 `TransferBattery` 强校验实际允许的目标组织类型和链路关系。
- 门店管理新增门店时不再拉组织树，直接以当前登录经销商作为只读上级组织。
- 组织创建后端增加 `parent_id` 校验，阻断绕过前端的越权创建。

## 2. 关键改动
### 2.1 电池调拨前端
- 文件：`frontend/src/views/bms/battery/list/index.vue`
- `transferOrgTypeOptions` 调整：
  - `DEALER -> STORE`
  - `STORE -> []`
- 门店账号保留“调拨”菜单项但标记 `disabled`，点击时只提示，不打开弹窗。
- 打开调拨弹窗前，若无可选目标类型直接阻断，不再默认回退到 `DEALER`。

### 2.2 电池调拨后端
- 文件：`backend/internal/service/battery_lifecycle.go`
- `TransferBattery` 调整：
  - `DEALER` 目标仅允许 `STORE`。
  - 去掉经销商到 `PACK_FACTORY` 分支校验逻辑。
  - `STORE` 分支改为直接拒绝“门店账号无调拨权限”。

### 2.3 门店管理前端
- 文件：`frontend/src/views/bms/org/modules/org-modal.vue`
- 新增“经销商新增门店”场景判定：
  - `fixedOrgType=STORE && currentUser.org_type=DEALER`
- 该场景下：
  - 预填 `parent_id = currentUser.org_id`
  - 上级组织控件改为只读 `NInput`
  - 不调用 `getOrgTree()`

### 2.4 门店创建后端
- 文件：`backend/internal/service/org.go`
- `CreateOrg` 增加校验：
  - 当 `TENANT_USER` 且当前机构类型为 `DEALER` 且 `req.OrgType=STORE` 时，
  - `req.ParentID` 必须存在且等于 `claims.OrgID`，否则拒绝。

## 3. 测试策略
- 后端：`go test ./internal/api ./internal/service`
- 前端：`eslint` 定向校验 + `pnpm build`
- 手工验证：
  - 经销商调拨仅门店；
  - 门店调拨禁用且后端拒绝；
  - 经销商新增门店不拉组织树且上级只读；
  - 经销商伪造 `parent_id` 创建门店被拒绝。
