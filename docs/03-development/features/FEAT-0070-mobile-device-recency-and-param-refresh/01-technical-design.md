# FEAT-0070 移动端设备最近连接排序与参数刷新 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-07-25
- related_feature: FEAT-0070
- version: v0.1.0

## 1. 数据与排序
- `devices` 新增可空 `last_connected_at TIMESTAMPTZ`，不为历史数据补值。
- BLE：`ReportBatteryConnectionStatusForApp` 在权限和连接类型校验通过、`ble_connected=true` 时记录服务端当前时间。
- 4G：`MarkFourGBatteryOnlineByInteraction` 仅在真实非 retained Socket 上行触发路径记录服务端当前时间；调用方已有 30 秒节流。
- 记录连接时间与在线状态变更解耦，即设备已在线时再次成功建立实时通讯仍可更新时间。
- 三种列表视图先将有成功通讯记录的设备按 `last_connected_at DESC NULLS LAST` 排在前面；仅对空时间设备使用原关系时间倒序：
  - 自绑定：空时间回退 `dub.binding_time DESC`
  - 我添加：空时间回退 `ar.added_at DESC`
  - 终端绑定：空时间回退 `lb.binding_time DESC`
- 设备 ID 始终作为最终升序键，保证相同时间下跨分页顺序稳定。
- 排序在后端 SQL 完成，保证跨分页全局顺序；接口 wire shape 不变。

## 2. 首页状态角标
- `device-card.vue` 增加 `showStatus` 派生状态：仅当设备是 4G/4G+BLE、当前非蓝牙连接且离线时返回 false。
- 模板用 `v-if` 移除整个角标；标题容器根据 `showStatus` 切换预留宽度。
- 4G 在线、BLE 连接、普通 MQTT/离线的文字、颜色和图标保持现有实现。

## 3. 参数刷新
- 四个基础分组头部右侧拆为“刷新按钮 + 折叠箭头”，刷新按钮仅在分组展开后显示。
- 刷新事件使用 `@tap.stop`，按钮最小 `88rpx × 88rpx`；加载时显示旋转态并忽略重复点击。
- `loadKeysCached(section, keys, force=false)` 在 `force=true` 时绕过 `loaded`。
- `loadKeys` 先在局部变量验证响应；至少一个允许 key 有非空值才提交到 `paramValues`。MQTT 空结果保留现有一次延迟重试，最终空结果返回失败。
- `refreshSection` 复用连接占用检查、MQTT 唤醒与 `loadSection(..., true)`；无论成功失败均保持展开，失败显示 `deviceDetail.toast.refreshFailed`。

## 4. 兼容与发布顺序
- 新增 `backend/sql/65.sql` 并同步 `backend/sql/1.sql`。
- 发布顺序：数据库增量 → 后端 → UniApp。
- 保持 FEAT-0069 当前未提交文件不变；FEAT-0070 后端修改限定在设备首页、APP 电池连接时间及新增 SQL/测试。
