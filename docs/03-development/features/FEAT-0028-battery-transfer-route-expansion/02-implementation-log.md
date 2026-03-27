# FEAT-0028 电池调拨路径扩展 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-03-27
- related_feature: FEAT-0028
- version: v0.1.0

## 1. 实施记录
1. 新建 FEAT-0028 文档目录，并在项目看板登记 Backend / Frontend 条目。
2. 调整 `backend/internal/service/battery_lifecycle.go`：
   - 经销商从“仅门店间调拨”改为“经销商库存 -> PACK/门店”。
   - 新增门店“门店库存 -> 经销商”能力。
3. 调整 `backend/internal/service/device_binding.go` 组织选项逻辑：
   - 经销商可获取上级 PACK 选项；
   - 门店可获取上级经销商选项。
4. 调整 `frontend/src/views/bms/battery/list/index.vue`：
   - 调拨弹窗目标类型按角色动态展示；
   - 打开弹窗时按允许类型自动设置默认目标并加载对应选项。

## 2. 当前状态
- 前后端代码已完成。
- 已完成定向 Go 校验与前端定向静态检查。
- 待联调验证三条新增业务链路。
