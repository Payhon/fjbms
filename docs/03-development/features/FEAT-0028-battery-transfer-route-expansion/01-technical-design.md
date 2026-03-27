# FEAT-0028 电池调拨路径扩展 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-03-27
- related_feature: FEAT-0028
- version: v0.1.0

## 1. 方案概览
本次调整分前后端两部分：
- 后端 `Battery.TransferBattery` 更新调拨权限矩阵与组织树校验。
- 后端 `DeviceBinding.GetOrgOptions` 扩展“上级组织”查询能力，供管理端调拨弹窗复用。
- 前端 `bms/battery/list` 调拨弹窗改为按当前账号角色动态展示目标机构类型。

## 2. 权限矩阵
- `BMS_FACTORY / SYS_ADMIN / TENANT_ADMIN`
  - 保持现状：仅处理 `PACK -> PACK/经销商`
- `PACK_FACTORY`
  - `PACK -> 经销商/门店`
- `DEALER`
  - `经销商 -> PACK`
  - `经销商 -> 门店`
- `STORE`
  - `门店 -> 经销商`

## 3. 组织树校验
- 下发到下级组织时，要求目标组织是当前组织的 descendant。
- 回退到上级组织时，要求目标组织是当前组织的 ancestor。
- 经销商回 PACK：目标 `PACK_FACTORY` 必须在当前经销商的上级链路中。
- 门店回经销商：目标 `DEALER` 必须在当前门店的上级链路中。

## 4. 前端交互
- 调拨弹窗目标类型动态收敛：
  - 厂家：admin/BMS 仅 `PACK厂 / 经销商`
  - PACK：`经销商 / 门店`
  - 经销商：`PACK厂 / 门店`
  - 门店：`经销商`
- 打开弹窗时自动选择当前角色允许的第一个目标类型，并加载对应机构选项。

## 5. 测试策略
- 后端：定向 `go test ./internal/service ./internal/api ./internal/dal`
- 前端：定向 ESLint 校验调拨页面
- 手工回归：
  - 经销商调拨回 PACK
  - 经销商调拨至门店
  - 门店调拨回经销商
  - 非法路径拒绝

## 6. 兼容性与迁移
- 不涉及数据库 schema 变更，无新增 SQL。
- 旧转移记录保留不变。
