# FEAT-0071 第三方 MES 批量重新分配 PACK 厂 - 功能规格

- status: review
- owner: payhon
- last_updated: 2026-07-28
- related_feature: FEAT-0071
- version: v0.2.0

## 1. 背景与目标

- 已有一批 BMS 板从 BMS 厂家出厂到尚未投入使用的 PACK 厂，需要由厂家重新分配给另一家 PACK 厂。
- Web 端逐批操作效率不足，第三方 MES 需要通过现有 OpenAPI 密钥直接批量完成重新分配。
- 接口必须以后端当前归属为来源，不接受 MES 指定原 PACK 厂，避免客户端提供过期来源信息。

## 2. 范围

### In Scope

- 新增 `POST /api/v1/openapi/mes/battery/reassign-pack-factory`。
- 使用 `x-app-id`、`x-secret-key` 鉴权，按密钥租户隔离数据。
- 按电池 SN 批量处理，目标 PACK 厂按租户内名称精确唯一匹配。
- 每台设备独立事务，允许部分成功并返回逐台结果。
- 同时更新当前持有组织与 PACK 组装方组织，写入组织转移和电池运营日志。
- 同步 Swagger、MES 文档、联调脚本和项目看板。

### Out of Scope

- 不新增 Web 或移动端入口。
- 不修改普通 Web 调拨接口和角色矩阵。
- 不新增数据库表、字段、API scope 或独立权限。
- 不自动处理已激活、已绑定用户或已完成 PACK 信息补全的设备。
- 不执行外部 API 密钥撤销或轮换。

## 3. 接口行为

- 请求字段：
  - `serial_numbers`：必填，1～500 条 SN；Trim 后按首次出现去重。
  - `target_pack_factory_name`：必填，租户内正常状态 `PACK_FACTORY` 名称精确唯一匹配。
  - `remark`：可选，最大 255 字符。
- 后端根据 `device_batteries.owner_org_id` 解析当前来源 PACK。
- 单台结果状态：
  - `REASSIGNED`：实际完成重新分配。
  - `UNCHANGED`：`owner_org_id` 与 `pack_factory_org_id` 已同时属于目标 PACK。
  - `FAILED`：不满足转移条件或单台事务失败。
- 请求级目标 PACK 或参数错误时不处理任何设备；设备级错误进入部分成功结果。

## 4. 验收标准

1. MES 仅提交 SN 列表、目标 PACK 厂名称和可选备注即可执行。
2. 目标 PACK 必须是当前租户内唯一、正常状态的 PACK 厂。
3. 仅允许当前属于 PACK 厂、未激活、无所有者绑定、流转状态为空或 `FACTORY`、未完成 PACK 信息补全的设备重新分配。
4. 成功时 `owner_org_id` 与 `pack_factory_org_id` 同时指向目标 PACK。
5. 已完全属于目标 PACK 的重复请求返回 `UNCHANGED`，且不重复写转移日志。
6. 当前持有 PACK 与非空 PACK 组装方字段不一致时拒绝自动修复。
7. 跨租户设备按不存在处理，不泄露其他租户信息。
8. 部分成功响应保留输入顺序，并返回总数、成功、未变化、失败和逐台原因。
9. 成功转移的业务更新、组织转移日志和运营日志处于同一事务。

## 5. 风险与约束

- 所有现有有效 MES OpenAPI 密钥均可调用本接口；本次不引入细粒度 scope。
- 接口属于高影响库存变更，必须限制批次大小、使用行锁并提供幂等结果。
- 文档中不得保留真实 AppId、SecretKey；已暴露密钥的实际轮换需由管理员另行完成。

## 6. 回滚方案

- 回滚新路由、控制器、请求模型和专用服务即可关闭入口。
- 独立操作类型为字符串，不需要回滚数据库结构。
- 已成功产生的组织转移记录不自动回退；如需业务恢复，应通过既有人工生命周期流程处理。
