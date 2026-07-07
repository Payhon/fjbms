# FEAT-0063 PACK 厂小程序配置自助入口 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-07-01
- related_feature: FEAT-0063
- version: v0.1.0

## 1. 测试范围
- 后端 PACK_FACTORY 账号小程序配置访问控制。
- SQL 61 菜单与机构类型权限迁移逻辑。
- Web 新自助页面、共享配置组件、旧 PACK 厂家管理弹窗复用。
- 路由、多语言和类型声明。

## 2. 测试环境
- 本地工作区：`/Users/payhon/work2025/project/fjbms`
- Backend 子仓：`backend`
- Web 子仓：`frontend`
- 测试环境：`1.95.190.254:22`，数据库 `fjbms`
- 生产环境：`120.78.228.241:22`，数据库 `fjiacloud`

## 3. 用例结果
| 用例 | 结果 | 说明 |
| --- | --- | --- |
| 后端定向测试：PACK_FACTORY 账号只能读写自己机构小程序配置 | 通过 | 纳入 `run_env=localdev go test -v ./internal/service/...`；新增用例 `TestPackFactoryUserCanOnlyManageOwnWxMpConfig` 通过 |
| 后端 service 包测试 | 通过 | `run_env=localdev go test -v ./internal/service/...` 通过；macOS 上游 `gopsutil` 仅输出 `IOMasterPort` deprecated warning |
| SQL 61 静态校验 | 通过 | 已核对 `org_type_permissions.ui_codes` 为 `jsonb`，菜单字段与既有迁移一致；迁移逻辑幂等新增 `bms_pack_wxmp_config` 并移除 PACK_FACTORY 的 `bms_pack_factory` |
| 测试环境 SQL 61 更新 | 通过 | `make import-sql ENV=test SQL=backend/sql/61.sql` 执行成功，输出 `DO`、`UPDATE 1`；只读校验 `menu_count=1`、`pack_total=1`、`pack_with_new=1`、`pack_with_old=0` |
| 生产环境 SQL 61 更新 | 通过 | `make import-sql ENV=prod SQL=backend/sql/61.sql` 执行成功，输出 `DO`、`UPDATE 1`；只读校验 `menu_count=1`、`pack_total=1`、`pack_with_new=1`、`pack_with_old=0` |
| Web 受影响文件 ESLint | 通过 | 共享组件、自助页面、旧弹窗、路由和类型声明无 ESLint error/warning |
| Web 显式类型检查过滤 | 通过 | `pnpm exec vue-tsc --noEmit --skipLibCheck --pretty false` 全量仍受既有 `build/plugins/router.ts`、`packages/axios`、`src/App.vue`、`src/card/**` 错误阻塞；本次受影响文件过滤后无报错 |
| `git diff --check` | 通过 | 根仓、backend、frontend 空白检查通过 |
| PACK_FACTORY 真实账号菜单与保存回归 | 待运行态回归 | 需目标后台账号 |
| TENANT_ADMIN/SYS_ADMIN 旧入口回归 | 待运行态回归 | 需目标后台账号 |

## 4. 缺陷与风险
- 暂无已知本次代码缺陷。
- Web 全量类型检查仍有仓库既有错误，当前结论以受影响文件过滤为准。
- PACK_FACTORY 账号菜单可见性和旧入口隐藏需要真实账号回归确认。

## 5. 结论
- 代码已进入 review。
- 本地后端测试、Web 定向 ESLint、受影响文件类型过滤、空白检查、测试环境 SQL 更新和生产环境 SQL 更新已完成。
- 仍需真实账号运行态验收。
