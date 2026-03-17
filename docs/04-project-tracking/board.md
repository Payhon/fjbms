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
- [ ] `in_progress` **FEAT-0016** 遗留 BMS 设备 UUID 自动补建
  - owner：payhon
  - 优先级：P1
  - 依赖：FEAT-0008
  - 进展：已完成规格/设计，正在实现 `provision/info` 可自注册返回结构、`provision/bind` 事务式懒注册，以及 UniApp 开通向导的遗留设备提示分支
  - 文档：`docs/03-development/features/FEAT-0016-legacy-device-auto-register/`
- [ ] `in_progress` **FEAT-0015** 后台用户体系与角色权限重构
  - owner：payhon
  - 优先级：P1
  - 依赖：FEAT-0010
  - 进展：已完成规格/设计，正在实施 `users.is_main`、`user_roles`、`role_permissions`、租户识别口径统一、登录权限叠加及后台账号/角色管理改造
  - 文档：`docs/03-development/features/FEAT-0015-backoffice-user-role-refactor/`
- [ ] `in_progress` **FEAT-0014** 电池信息补全（电芯品牌/电池型号）
  - owner：payhon
  - 优先级：P1
  - 依赖：FEAT-0012
  - 进展：已完成规格/设计，已实现 `device_batteries` 新字段、信息补全接口、电池列表筛选与展示、权限点、原地新增型号组件及运营日志接入，并补充电池详情页 `基本信息` 标签页、列表 `编辑 BMS 信息/删除` 操作、产品规格列与固定列体验优化
  - 文档：`docs/03-development/features/FEAT-0014-battery-info-completion/`
- [ ] `review` **FEAT-0012** BMS 历史数据查询与异步导出通知
  - owner：payhon
  - 优先级：P1
  - 依赖：FEAT-0010
  - 进展：已完成前后端与 SQL 实现，已完成定向编译与静态检查，待联调验收（导出任务全链路）
  - 文档：`docs/03-development/features/FEAT-0012-bms-history-data-export/`
- [ ] `in_progress` **FEAT-0012** 电芯品牌管理 + PACK电池型号管理（行内增删改）
  - owner：payhon
  - 优先级：P1
  - 依赖：FEAT-0010
  - 进展：已完成 `battery_models -> battery_bms_models` 拆分迁移、后端关联逻辑改造（单个新增/导入/OTA 回查兼容）、前端行内增删改页面与菜单文案（新增BMS），并新增「BMS型号管理」菜单与 CRUD；待测试环境执行 SQL 并完成租户联调验收
  - 文档：`docs/03-development/features/FEAT-0012-cell-brand-battery-model-management/`
- [ ] `in_progress` **FEAT-0011** 电池列表详情路由与页面元素权限补齐
  - owner：payhon
  - 优先级：P1
  - 依赖：FEAT-0010
  - 进展：已完成后端 `ui_codes/me` 接口、详情路由/按钮权限 SQL、前端指令显隐/禁用；已修复“电池列表误跳详情页/仅电池列表权限空白页”问题，待联调租户数据与回归验收
  - 文档：`docs/03-development/features/FEAT-0011-battery-list-detail-element-permission/`
- [ ] `in_progress` **FEAT-0010** 机构类型菜单权限生效与首页分层改造
  - owner：payhon
  - 优先级：P1
  - 依赖：无
  - 进展：已完成菜单权限生效、首页分层、权限回显修复、组织快捷菜单独立页面改造，以及首页身份展示/管理员视角切换与看板告警接口修复，待执行 SQL 补丁并完成联调验收
  - 文档：`docs/03-development/features/FEAT-0010-org-permission-home-segmentation/`
- [ ] `in_progress` **FEAT-0007** 蓝牙 BMS 经 App 上云 + 后台 BMS 实时/历史可视化
  - owner：payhon
  - 优先级：P1
  - 依赖：无
  - 进展：已完成 APP 上云、云端可视化与 BLE Relay，并新增“APP 连接态同步设备在线状态（含蓝牙断开主动离线）”，当前进行真机联调验收
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
- [ ] `in_progress` **FEAT-0009** 管理端登录验证码与二维码配置展示
  - owner：payhon
  - 优先级：P1
  - 依赖：无
  - 进展：已完成规格/设计，正在实现前后端与数据库迁移
  - 文档：`docs/03-development/features/FEAT-0009-admin-login-captcha-qrcode/`

### UniApp（`fjbms-uniapp/`）
- [ ] `in_progress` **FEAT-0016** 遗留 BMS 设备 UUID 自动补建
  - owner：payhon
  - 优先级：P1
  - 依赖：FEAT-0008
  - 进展：已完成规格/设计，待接入“设备不存在但可自动注册”的提示与继续绑定分支
  - 文档：`docs/03-development/features/FEAT-0016-legacy-device-auto-register/`
- [ ] `in_progress` **FEAT-0013** 移动端设备添加分流、首页视图切换与筛选增强
  - owner：payhon
  - 优先级：P1
  - 依赖：FEAT-0010
  - 进展：已完成数据库迁移、后端按用户类型分流、首页 `view_mode` 查询、机构移除接口，以及 UniApp 我的页切换入口和首页筛选/分页/模式菜单改造；待执行 SQL、真机联调和端到端验收
  - 文档：`docs/03-development/features/FEAT-0013-mobile-device-view-mode-and-filter/`
- [ ] `in_progress` **FEAT-0006** 升级检测与提示体验优化
  - owner：待指派
  - 优先级：P1
  - 依赖：无
  - 文档：`docs/03-development/features/FEAT-0006-uniapp-upgrade-ux/`
- [ ] `in_progress` **FEAT-0008** 蓝牙信号图标展示与手动断开连接
  - owner：payhon
  - 优先级：P1
  - 依赖：无
  - 文档：`docs/03-development/features/FEAT-0008-uniapp-ble-disconnect-ux/`

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
