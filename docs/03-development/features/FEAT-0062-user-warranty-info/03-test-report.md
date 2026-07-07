# FEAT-0062 用户质保信息与 PACK 质保卡片开关 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-07-01
- related_feature: FEAT-0062
- version: v0.1.0

## 1. 测试范围
- 后端 PACK 小程序配置开关、移动端质保 profile、电池质保查询/编辑和激活计算。
- Web PACK 配置弹窗、电池详情质保 Tab 和 API 类型。
- UniApp 质保信息页、菜单入口和 AppID 请求。
- 文档与看板同步。

## 2. 测试环境
- 本地工作区：`/Users/payhon/work2025/project/fjbms`
- Backend 子仓：`backend`
- Web 子仓：`frontend`
- UniApp 子仓：`fjbms-uniapp`

## 3. 用例结果
| 用例 | 结果 | 说明 |
| --- | --- | --- |
| 后端定向测试：PACK 配置默认值、质保卡片隐藏、激活计算、人工覆盖保护、开通向导绑定激活 | 通过 | 纳入 `./internal/service/...` 执行；macOS 上游 `gopsutil` 仅输出 `IOMasterPort` deprecated warning |
| `run_env=localdev go test -v ./internal/service/...` | 通过 | 后端 service 包测试通过 |
| Web 显式 `pnpm exec vue-tsc --noEmit --skipLibCheck --pretty false` | 未通过 | 仓库既有全量类型错误阻塞，首批来自 `build/plugins/router.ts`、`packages/axios/src/index.ts`、`src/App.vue`、`src/card/**` 等；本次受影响文件过滤后无报错 |
| Web 受影响文件 ESLint | 通过 | `src/service/api/bms.ts`、PACK 配置弹窗、设备详情页、质保 Tab 无 ESLint error；PACK 配置弹窗存在既有 Prettier warning，不影响退出码 |
| UniApp `pnpm exec tsc -p tsconfig.json --noEmit --skipLibCheck` | 通过 | UniApp TypeScript 检查通过 |
| UniApp 质保页 UI 优化后 TypeScript 复测 | 通过 | `pnpm exec tsc -p tsconfig.json --noEmit --skipLibCheck` 通过；覆盖个人信息只读/编辑态、拟物化电池卡片模板，以及编号、型号、质保时长排版调整 |
| UniApp 我的页质保图标替换后 TypeScript 复测 | 通过 | `pnpm exec tsc -p tsconfig.json --noEmit --skipLibCheck` 通过；新增 `static/image/my/icon-warranty@2x.png` 并替换“质保信息”菜单图标引用 |
| UniApp 受影响文件 ESLint | 不适用 | 当前 UniApp 工作区未安装可执行 `eslint`，`pnpm exec eslint ...` 返回 `Command "eslint" not found` |
| `git diff --check` | 通过 | 根仓、backend、frontend、fjbms-uniapp 四个工作树空白检查通过 |
| `make import-sql ENV=test SQL=backend/sql/60.sql` | 通过 | 测试环境 SQL 执行成功，远端返回 `CREATE TABLE`、`ALTER TABLE`、`DO` 和权限补齐 `UPDATE` |
| `make import-sql ENV=prod SQL=backend/sql/60.sql` | 通过 | 生产环境 SQL 执行成功，远端返回 `CREATE TABLE`、`ALTER TABLE`、`DO` 和权限补齐 `UPDATE` |
| 测试/生产只读结构校验 | 通过 | 两个环境均确认 `user_warranty_infos`、`device_batteries` 质保列、`pack_wxmp_configs.warranty_cards_enabled`、`bms_battery_detail_warranty` 和 `bms_pack_factory` 权限存在 |
| PACK_FACTORY 后台账号只能配置自己组织 | 待运行态回归 | 需目标后台账号 |
| PACK 小程序开关开启/关闭真机展示 | 待运行态回归 | 需微信开发者工具或真机小程序 |

## 4. 缺陷与风险
- 暂无已知代码缺陷。
- Web 与 UniApp 静态检查结果以本地最终验证为准。
- 运行态权限和小程序展示依赖目标账号与目标 AppID，需要上线前补充人工验收。

## 5. 结论
- 代码已进入 review。
- 数据库 SQL、后端接口、Web、UniApp 和文档已同步。
