# FEAT-0070 移动端设备最近连接排序与参数刷新 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-07-25
- related_feature: FEAT-0070
- version: v0.1.0

## 1. 实施记录
- 2026-07-25：创建功能规格、技术设计、测试报告和发布说明；规格与设计进入 `approved`。
- 2026-07-25：看板进入 `in_progress`。
- 2026-07-25：新增 `backend/sql/65.sql` 并同步基线、GORM model/query，增加 `devices.last_connected_at`。
- 2026-07-25：BLE 成功连接上报与 4G Socket 真实交互接入服务端时间写入；断开、失败和 retained 回包路径不写入。
- 2026-07-25：三种 APP 首页视图改为“有通讯时间优先、时间倒序；空时间按原关系时间倒序；设备 ID 最终稳定排序”。
- 2026-07-25：4G/4G+BLE 离线卡片移除整个状态角标并释放标题空间，其他状态保持原样。
- 2026-07-25：四个基础参数分组增加 `88rpx` 刷新热区、加载旋转态、事件阻止与 `force` 缓存旁路；空响应不再写入缓存或覆盖旧值。
- 2026-07-25：补齐中英文刷新标签和失败提示，完成后端定向测试、UniApp TypeScript/策略测试与差异检查；看板转入 `review`。

## 2. 变更文件
- 后端：`internal/service/app_battery.go`、`app_device_home.go`、`device_last_connected.go` 及对应测试。
- 数据：`sql/65.sql`、`sql/1.sql`、设备 model/query。
- UniApp：`components/home/device-card.vue`、`pages/device-battery/components/params-tab.vue`、状态/刷新策略与中英文词包。

## 3. 待验收
- 微信小程序、iOS、Android 真机角标、触控热区、加载动画与 BLE/4G 排序验证。
- 真实 PostgreSQL 执行 `sql/65.sql` 后核对字段和三类列表分页。

## 4. 风险与回滚
- 发布必须先执行 SQL；回滚优先回滚后端排序与 UniApp 展示，新增可空字段允许保留。
- FEAT-0069 原有未提交修改均保留；本功能未覆盖或重置其后端、前端和文档变更。
