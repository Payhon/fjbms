# FEAT-0075 测试报告

- status: review
- owner: payhon
- last_updated: 2026-09-28
- related_feature: FEAT-0075
- version: v0.1.0

## 1. 测试范围与环境

本地实现阶段使用 macOS 工作区、UniApp、Vue 3、TypeScript、HBuilderX 5.26、Web Vue 3/Vite、后端现有 SQLite 测试辅助及独立 PostgreSQL 16 Alpine 容器（未映射宿主机端口）。用户于 2026-09-28 追加授权部署后，另对测试与生产环境 PostgreSQL 14.12、后端进程、Web 产物和公网页面进行校验，结果与本地检查分列。

## 2. 本地检查

| 检查 | 结果 | 证据与边界 |
| --- | --- | --- |
| 两端授权/拒绝/空权限/失败/延迟与整卡片渲染 | 通过 | `node pages/device-battery/protection-status-permission.test.js`，执行实际 SFC 加载函数和卡片模板；API 响应隔离模拟 |
| 历史记录权限独立、卸载后的迟到响应 | 通过 | 同一行为检查，历史记录单独授权仍显示，保护授权不带出历史记录 |
| 终端用户/机构用户权限隔离 | 通过 | `go test ./internal/service -run 'Test(MobileProtectionStatusPermissionIsolation|NormalizeDeviceParamPermissionKeys|BuildDeviceParamPermissionTreeUsesCanonicalKeys)$' -count=1`；现有服务实际读取测试配置，变更后重新读取 |
| SQL 67 与 SQL 1 注册块 | 通过 | SQL 1 末尾与 67 完全一致；隔离 PostgreSQL 内有根节点/无根节点两种情形各重复执行两次，节点唯一、复用已有根 ID、原历史节点和授权快照均不变 |
| UniApp TypeScript | 通过 | `pnpm exec tsc --noEmit --pretty false` |
| UniApp 两个受影响 SFC | 通过 | `@vue/compiler-sfc` script/template 编译 |
| 微信小程序编译 | 通过 | HBuilderX 5.26 `launch mp-weixin --compile true --continue-on-error false`；前端编译成功，产物含布尔属性和整个卡片的条件分支 |
| Web 受影响文件 ESLint | 通过 | `pnpm exec eslint src/service/api/org-type-permissions.ts src/views/device/details/modules/bms-panel/index.vue` |
| 扫码返回/仪表会话恢复回归 | 通过 | `node pages/device-provision/ble-scan-auto-start.test.js`、`pnpm dlx tsx pages/device-battery/instrument-session-recovery.test.js` |
| Web 全量显式类型检查 | 未通过（既有错误） | `pnpm exec vue-tsc --noEmit --skipLibCheck --pretty false`；HEAD 只读覆盖基线与本次结果均为 1781 条诊断，按文件位置及错误编码比较无新增，两份受影响文件无诊断 |
| Web 构建 | 通过 | `pnpm build` 退出 0，输出 `Build successful`；其类型脚本在 macOS 下不能证明显式类型通过 |

## 3. 浏览器与真机验收

| 验收 | 状态 | 边界 |
| --- | --- | --- |
| 隔离浏览器显示/隐藏与展开交互 | 通过 | Playwright + 两端实际卡片模板、加载/展开函数；加载中和重新加载时两端容器数均为 0，授权后各 1、展开后各 2 行，取消与失败后均为 0；取消保护权限时历史仍为 true，失败时历史为 false |
| 真实后台勾选保存、取消勾选、重新进入详情 | 待验收 | SQL 67 与 Web 已部署，两环境原有授权保持不变；当前未执行真实账号授权配置操作 |
| 微信小程序真机 | 待验收 | 编译成功不等于真机验收 |
| Android App | 待验收 | `adb devices -l` 无调试设备 |
| iOS App | 待验收 | `xcrun devicectl list devices` 中两台手机均为 unavailable |

## 4. 缺陷与风险

HBuilderX 提示现有 uniCloud 本地服务空间不存在，前端编译仍成功。Go 构建有现有 macOS IOMasterPort 弃用警告，不影响定向测试。

Web 的 `pnpm typecheck` 脚本使用 Windows `set` 写法，在 macOS 下不能用其退出成功证明类型通过，必须以显式 `vue-tsc` 结果为准。已有错误包括路由插件 `layoutOptions` 和 Axios 错误对象类型，本次未扩大修复范围。构建还有现有组件命名冲突、图标缺失和 Node localStorage 提示，构建完成。

隔离浏览器测试使用原卡片模板和事件函数，Naive UI 外围组件与权限响应替换为本地替身。验证显隐和 DOM 移除，不等于真实后台保存链路或原生 App 布局、事件验收。浏览器无 error，模拟请求失败产生一条预期权限加载 warning。

## 5. 验证记录与待验收步骤

- 隔离浏览器授权截图：[feat0075-authorized.png](/Users/payhon/work2025/project/fjbms/docs/03-development/features/FEAT-0075-bms-protection-status-permission/evidence/feat0075-authorized.png)。未授权截图：[feat0075-denied.png](/Users/payhon/work2025/project/fjbms/docs/03-development/features/FEAT-0075-bms-protection-status-permission/evidence/feat0075-denied.png)。
- 类型基线对比：[web-typecheck-comparison.json](/Users/payhon/work2025/project/fjbms/docs/03-development/features/FEAT-0075-bms-protection-status-permission/evidence/web-typecheck-comparison.json)。记录诊断数量、位置/错误编码差集及受影响文件诊断；类型信息的打印顺序不作为差异。
- PostgreSQL 隔离验证的实际输入：[permission-registration-check.sql](/Users/payhon/work2025/project/fjbms/docs/03-development/features/FEAT-0075-bms-protection-status-permission/evidence/permission-registration-check.sql)。仅供空白测试数据库执行，包含测试表、授权快照与断言，不能作为生产迁移；生产只使用 `backend/sql/67.sql`。
- 待真实验收：分别对 `APP_USER` 和一个机构类型勾选/保存后重新进入详情，确认完整卡片可展开；只取消其中一类，确认该类整块隐藏、另一类仍显示；单独调整历史记录权限，确认历史 Tab 与保护区块互不影响；检查顶部故障/告警/保护提示保持原行为。微信小程序、Android 和 iOS 各执行一次并记录设备及版本。

## 6. 2026-09-28 部署校验

| 检查 | 生产 | 测试 |
| --- | --- | --- |
| 数据库迁移 | SQL 67 完成，新权限节点唯一且父节点正确 | SQL 66 前置依赖和 SQL 67 完成，新权限节点唯一且父节点正确 |
| 原有授权及设备绑定 | 事务内快照断言通过，机构授权摘要不变 | 事务内快照断言通过，机构授权摘要不变 |
| 后端二进制/配置 | SHA-256 与冻结产物一致，配置不变，保留原进程 | 后端已替换并重启，SHA-256 一致，配置不变 |
| 后端运行 | active/running，PID 649159，`/health` 200 | PID 3617484，MQTT 被拒绝，未监听 HTTP，`/health` 无响应 |
| Web / 权限代码文件 | 公网 200，SHA-256 与生产构建一致 | 公网 200，SHA-256 与测试构建一致 |
| 匿名权限接口 | 本机与公网均 401，认证仍生效 | 本机无响应，公网 502，未通过运行验收 |
| 发布备份 | 数据库自定义格式、旧二进制和 Web 归档校验通过 | 数据库自定义格式、旧二进制和 Web 归档校验通过 |
| 真实浏览器登录页 | 页面正常，控制台无 error | 页面渲染，但 logo/sys_function/captcha 请求 502 |

测试环境启动失败在部署前已存在。运行配置指向 pbsmart 项目的 `127.0.0.1:1883`，其认证回调为 `http://java:8080/iot/tool/mqtt/authv5`；后端日志每 5 秒出现 `MQTT Adapter connection failed, retrying... error=not Authorized`。已请求用户确认 fjbms 测试专用 Broker 地址或配置文件路径，未修改共享 Broker 认证规则。测试服务恢复与功能验收仍待完成。

后端部署前定向回归 `go test ./internal/service ./internal/api ./router/apps` 全部通过；Web `pnpm build:test`、`pnpm build` 完成。发布依据沿用上文“全量类型既有错误无新增”的局部门禁，不能将构建成功记为全量类型检查通过。

部署明细及校验和：[deployment-verification.json](/Users/payhon/work2025/project/fjbms/docs/03-development/features/FEAT-0075-bms-protection-status-permission/evidence/deployment-verification.json)。生产登录页截图：[prod-login-after-deploy.png](/Users/payhon/work2025/project/fjbms/docs/03-development/features/FEAT-0075-bms-protection-status-permission/evidence/prod-login-after-deploy.png)。测试登录页截图：[test-login-after-deploy.png](/Users/payhon/work2025/project/fjbms/docs/03-development/features/FEAT-0075-bms-protection-status-permission/evidence/test-login-after-deploy.png)。登录页冒烟与真实授权保存/详情验收分开记录。

## 7. 结论

局部代码、SQL 和本地验证已完成，生产 SQL/Web 已更新并通过运行校验；测试 SQL、后端文件和 Web 已更新，但服务可用性受既有 MQTT 认证依赖阻塞。Web 全量类型门禁、真实后台授权操作及真机验收尚未通过或完成，保持 `review`。本次未提交、推送或发布移动端。


## 2026-10-09 Git 交付前复核

- 重新运行两端实际权限加载函数/模板回归、后端服务/API 测试、UniApp TypeScript 及两平台分支 SFC 编译，全部通过。
- Web 两个修改文件的 ESLint 与 `pnpm build` 通过。显式 `vue-tsc --noEmit --skipLibCheck --pretty false` 仍为 1781 条诊断；以 HEAD 源码只读覆盖的基线同为 1781 条，按位置/编码比较无新增或移除，两份修改文件均无诊断。
- SQL 67 与初始化 SQL 1 注册块一致性复核通过；本轮未重跑 PostgreSQL 集成迁移或访问部署环境，2026-09-28 的部署证据保留为历史记录。
- 本轮按用户授权拆分 Git 提交并推送；未重新打包/发布移动端、部署服务或操作数据库，真机验收和功能状态保持原记录。
