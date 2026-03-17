# FEAT-0013 移动端设备添加分流、首页视图切换与筛选增强 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-03-12
- related_feature: FEAT-0013
- version: v0.1.0

## 日志
1. 2026-03-12 方案确认
   - 已确认按用户类型拆分移动端设备添加语义：
     - `END_USER`：绑定 + 激活
     - `ORG_USER`：仅加入“我的设备”
   - 已确认机构用户首页支持两种查看模式：
     - 我添加的设备
     - 终端用户绑定设备
2. 2026-03-12 文档落地
   - 新增 FEAT-0013 规格文档、技术设计、实施日志、测试报告、发布说明。
   - 看板新增 FEAT-0013，状态标记为 `approved`。
3. 2026-03-12 数据库迁移与后端主流程实现
   - 新增 SQL 迁移 `backend/sql/43.sql`，创建 `app_device_added_records` 表，用于承载机构账号“我添加的设备”记录。
   - `backend/internal/service/device_provision.go` 已按 `user_kind` 分流：
     - `END_USER` 保持绑定并激活；
     - `ORG_USER` 仅写入/更新 `app_device_added_records`，不绑定、不激活。
   - `backend/internal/service/device_binding.go` 已限制 `BindDevice` / `UnbindDevice` 仅终端用户可执行，并将首页列表查询切换为按 `view_mode` 分流。
   - 新增 `backend/internal/service/app_device_home.go`，统一承载 `self_bound` / `org_added` / `end_user_bound` 三种首页设备视图的查询、筛选与机构权限范围控制。
   - `backend/internal/api/device_binding.go` 与 `backend/router/apps/device_binding.go` 已新增机构用户“移除我添加的设备”接口 `POST /api/v1/app/device/remove`。
   - `backend/internal/service/activation_log.go` 已补充 `END_USER` 过滤，避免机构用户“仅添加”被记入激活日志。
4. 2026-03-12 UniApp 首页与我的页改造
   - 新增 `fjbms-uniapp/common/device-view-mode.ts`，统一管理首页视图模式枚举、本地持久化和机构用户默认模式。
   - `fjbms-uniapp/pages/my/my.vue` 已在设置图标旁新增机构用户专属视图切换入口，并联动设备数量统计与模式标签文案。
   - `fjbms-uniapp/pages/home/home.vue` 已改为服务端分页、模式标签、筛选弹层和按模式区分长按菜单动作。
   - `fjbms-uniapp/store/bound-devices.ts` 已加入 `viewMode` 维度，避免不同首页模式共用旧缓存。
   - `fjbms-uniapp/service/device.ts`、`fjbms-uniapp/lang/zh-CN.ts`、`fjbms-uniapp/lang/en-US.ts` 已补齐新接口参数、移除动作和多语言文案。
5. 当前待办
   - 真机/模拟器联调：
     - 机构用户首页模式切换后的列表、筛选与只读行为；
     - 终端用户重命名/解绑回归；
     - 蓝牙添加后首页列表与本地缓存一致性。
   - 数据库环境执行 `backend/sql/43.sql` 后完成端到端验收。
6. 2026-03-12 回归修复：终端用户首页空列表
   - 现象：终端用户访问 `/api/v1/app/device/list?view_mode=self_bound` 时返回 `query_user_org_type` 数据库错误，根因是公共权限服务 `GetUserOrgType()` 将 `users.org_id` 的 `NULL` 值直接扫描到 `string`。
   - 修复：`backend/internal/service/org_type_permissions.go` 已改为使用 `sql.NullString` 读取 `org_id` 与 `user_kind`，终端用户无组织归属时按空组织处理，不再中断首页列表查询。
7. 2026-03-12 回归修复：`undefined` 查询参数导致首页列表被误筛空
   - 现象：移动端首页请求 `/api/v1/app/device/list` 时附带 `device_name=undefined`、`device_number=undefined`、`ble_mac=undefined` 等查询参数，后端将其视为真实筛选值，最终命中 `ILIKE '%undefined%'` 导致已有设备被过滤。
   - 修复：`fjbms-uniapp/service/device.ts` 已在发起列表请求前剔除空值、`undefined`、`null` 字符串；`backend/internal/service/app_device_home.go` 已同步把这类伪值按空值处理，避免旧端或异常请求再次误伤查询结果。
8. 2026-03-12 回归修复：移动端账号登录补充图形验证码
   - 现象：后端 `/api/v1/login` 已强制要求 `captcha_id` 与 `captcha_code`，UniApp 登录页仍沿用旧密码登录表单，导致账号密码登录直接返回 `Field 'CaptchaID' is required`。
   - 修复：`fjbms-uniapp/pages/login/login.vue` 已新增图形验证码输入框、验证码图片展示与点击刷新；`fjbms-uniapp/service/app-auth.ts` 已补充 `/api/v1/login/captcha` 拉取与登录时携带 `captcha_id/captcha_code`。
9. 2026-03-12 回归修复：机构设备页查询参数 `undefined` 导致列表为空
   - 现象：机构用户访问“我的 > 机构设备”时，前端请求 `/api/v1/app/device/org/list` 携带 `device_number=undefined`、`owner_org_id=undefined`、`owner_org_type=undefined`，后端将其视为真实筛选值，导致设备列表被误筛空。
   - 修复：`fjbms-uniapp/service/device.ts` 已在 `appOrgDeviceList()` 中剔除空值、`undefined`、`null` 字符串；`backend/internal/service/device_binding.go` 已同步把组织设备查询中的同类伪值按空值处理。
10. 2026-03-12 蓝牙搜索页布局优化
   - 现象：蓝牙搜索过程中，顶部雷达动画区域会随着页面滚动离开视口，导致“扫描效果不显示”的体验问题；同时设备列表区域高度不固定。
   - 修复：`fjbms-uniapp/pages/device-provision/ble-scan.vue` 已调整为纵向固定布局，顶部雷达区、提示区与操作按钮固定显示，仅设备列表区域独立滚动，列表容器高度由页面剩余空间自动固定。
