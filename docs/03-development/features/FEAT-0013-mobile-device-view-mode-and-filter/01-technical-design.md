# FEAT-0013 移动端设备添加分流、首页视图切换与筛选增强 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-12
- related_feature: FEAT-0013
- version: v0.1.0

## 1. 方案概览
- 以“设备激活/绑定”和“首页可见性”解耦为核心思路：
  - `END_USER`：继续沿用 `device_user_bindings` 作为绑定与激活入口。
  - `ORG_USER`：新增“我添加的设备”记录表，仅表达当前机构账号想在首页看到该设备，不代表绑定或激活。
- 首页设备列表统一收敛为一个按 `view_mode` 查询的接口：
  - `self_bound`：终端用户自己的绑定设备。
  - `org_added`：机构用户自己添加的设备。
  - `end_user_bound`：机构用户权限范围内终端用户已绑定设备。
- “我的”页面新增模式切换入口；首页根据当前模式渲染标签、筛选条件与长按操作。

## 2. 接口与数据结构
### 2.1 新增数据表
- 建议新增表：`app_device_added_records`
- 字段建议：
  - `id`
  - `tenant_id`
  - `user_id`
  - `device_id`
  - `source`：`BLE_SCAN` / `UUID_SCAN`
  - `added_at`
  - `last_seen_at`
  - `remark` 或 `alias_name`（预留，可后续决定是否启用）
- 约束建议：
  - 唯一键：`(user_id, device_id)`
  - 索引：`(tenant_id, user_id, added_at desc)`、`(tenant_id, device_id)`

### 2.2 统一首页列表接口
- 接口：`GET /api/v1/app/device/list`
- 参数建议：
  - `view_mode`
  - `page`
  - `page_size`
  - `device_name`
  - `device_number`
  - `ble_mac`
  - `added_start_at`
  - `added_end_at`
- 权限规则：
  - `END_USER`：仅允许 `view_mode=self_bound`
  - `ORG_USER`：允许 `org_added` / `end_user_bound`
- 返回字段建议统一包含：
  - `device_id`
  - `device_name`
  - `device_number`
  - `ble_mac`
  - `bms_comm_type`
  - `is_online`
  - `activation_status`
  - `relation_type`：`BINDING` / `ORG_ADDED` / `END_USER_BOUND`
  - `binding_time` 或 `added_at`
  - 可选 `owner_end_user_name` / `owner_end_user_phone`（仅 `end_user_bound` 视图预留）

### 2.3 添加接口分流
- 现有接口：`POST /api/v1/app/device/provision/bind`
- 调整为按 `user_kind` 分流：
  - `END_USER`：
    - 复用现有绑定与激活逻辑；
    - 更新 `device_user_bindings`、`device_batteries.activation_status`、`devices.activate_flag`。
  - `ORG_USER`：
    - 校验租户与组织范围；
    - 写入或幂等更新 `app_device_added_records`；
    - 不写 `device_user_bindings`；
    - 不更新激活状态。

### 2.4 机构用户移除接口
- 建议新增接口：`POST /api/v1/app/device/remove`
- 用于删除当前机构账号的“我添加的设备”记录。
- 不复用 `unbind`，避免“移除首页可见性”与“解绑设备”概念混淆。

## 3. 关键流程
### 3.1 终端用户添加设备
1. 前端发起扫码/蓝牙添加。
2. 后端识别 `user_kind=END_USER`。
3. 校验设备归属与租户。
4. 创建设备绑定关系。
5. 更新设备激活状态。
6. 首页 `self_bound` 视图可见。

### 3.2 机构用户添加设备
1. 前端发起扫码/蓝牙添加。
2. 后端识别 `user_kind=ORG_USER`。
3. 校验设备在当前机构可访问组织范围内。
4. 写入或更新 `app_device_added_records`。
5. 不修改设备激活状态与绑定关系。
6. 首页 `org_added` 视图可见。

### 3.3 机构用户切换首页视图
1. 在“我的”页面点击设置旁切换图标。
2. 选择 `我添加的设备` 或 `终端用户绑定设备`。
3. 前端将模式持久化到本地存储。
4. 首页读取模式并调用统一列表接口重新拉取数据。

### 3.4 首页筛选
- 终端用户 `self_bound`：
  - `device_name`
  - `device_number`
  - `ble_mac`
- 机构用户 `org_added`：
  - `added_start_at` / `added_end_at`
  - `device_number`
  - `ble_mac`
- 机构用户 `end_user_bound`：
  - `device_name`
  - `device_number`
  - `ble_mac`

## 4. 安全与权限
- `END_USER` 仅能查看和操作自己的绑定设备。
- `ORG_USER` 的 `org_added` 仅能操作自己的添加记录。
- `ORG_USER` 的 `end_user_bound` 仅能查看当前组织树权限范围内设备，不能越权查看其它组织绑定数据。
- 管理员账号保持原有更高权限，但移动端首页仍建议按机构用户视图能力执行，避免移动端出现额外越权入口。

## 5. 测试策略
- 后端：
  - 新增用户类型分流测试。
  - 新增首页 `view_mode` 查询测试。
  - 新增机构范围过滤测试。
  - 新增“机构添加不激活、不记激活日志”测试。
- UniApp：
  - 类型检查。
  - 视图切换图标显示/隐藏与模式持久化验证。
  - 首页筛选弹层交互验证。
  - 不同模式下卡片菜单动作验证。
- 手工验收：
  - 终端用户添加/筛选。
  - 机构用户添加/移除。
  - 机构用户切换查看终端绑定设备。
  - 激活日志口径验证。

## 6. 兼容性与迁移
- 兼容现有 `device_user_bindings` 与激活统计口径，不修改历史终端绑定数据。
- 首页接口虽继续使用 `/api/v1/app/device/list`，但内部改为 `view_mode` 驱动；旧前端若不传 `view_mode`，建议后端按用户类型给默认值：
  - `END_USER` 默认 `self_bound`
  - `ORG_USER` 默认 `org_added`
- 激活日志查询逻辑需增加 `END_USER` 过滤，避免将机构用户“仅添加”误算为激活。
- 当前首页缓存与逐条遥测查询策略不适合大列表场景，FEAT-0013 落地时需同步切换为分页与服务端筛选，避免机构用户性能退化。
