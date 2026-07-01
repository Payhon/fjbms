# FEAT-0061 设备详情充放电控制工厂命令 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-06-25
- related_feature: FEAT-0061
- version: v0.1.0

## 1. 测试范围
- 后端设备参数权限树。
- Web BMS 设备详情高级设置工厂命令。
- UniApp 设备详情高级参数出厂配置。
- 命令字与协议示例帧一致性。

## 2. 测试环境
- 本地工作区：`/Users/payhon/work2025/project/fjbms`
- Backend 子仓：`backend`
- Web 子仓：`frontend`
- UniApp 子仓：`fjbms-uniapp`

## 3. 用例结果
| 用例 | 结果 | 说明 |
| --- | --- | --- |
| `go test ./internal/service -run 'TestNormalizeDeviceParamPermissionKeys|TestBuildDeviceParamPermissionTreeUsesCanonicalKeys'` | 通过 | 后端权限树与 key 归一化通过；macOS 上游 `gopsutil` 仅输出 `IOMasterPort` deprecated warning |
| `pnpm typecheck` | 不作为有效结论 | 脚本在 macOS 上使用 Windows 风格 `set NODE_OPTIONS=...`，命令退出 0 但不能作为显式 `vue-tsc` 结果 |
| `NODE_OPTIONS=--max-old-space-size=4096 pnpm exec vue-tsc --noEmit --skipLibCheck` | 未通过 | 仓库既有全量类型错误阻塞，首批错误来自 `build/plugins/router.ts`、`packages/axios/src/index.ts`、`src/App.vue`、`src/card/**` 等非本次修改文件 |
| 显式 `vue-tsc` 输出过滤受影响 Web 文件 | 通过 | 未发现 `src/views/device/details/modules/bms-panel/index.vue` 或 `src/locales/langs/*/bms.json` 相关报错 |
| `pnpm exec eslint src/views/device/details/modules/bms-panel/index.vue` | 通过 | Web 受影响 Vue 文件 ESLint 通过 |
| `pnpm exec tsc --noEmit --pretty false` | 通过 | UniApp TypeScript 检查通过 |
| `git diff --check` | 通过 | 根仓库、backend、frontend、fjbms-uniapp 四个工作树空白检查通过 |
| 协议帧校验 | 通过 | 本地按现有 CRC 口径确认三项命令字生成帧与需求一致：`0x80000000`、`0x40000000`、`0x00000000` |
| 受限账号权限显隐 | 待运行态回归 | 需后台账号和目标设备运行环境 |
| 真实设备命令下发 | 待运行态回归 | 需真实设备或联调链路 |

## 4. 缺陷与风险
- 暂无已知代码缺陷。
- 本地静态校验不能替代真实设备执行高风险命令的运行态验收。

## 5. 结论
- 本地定向校验通过，进入 review。
- Web 显式全量 typecheck 当前仍被仓库既有错误阻塞，需另行治理；本次修改文件未出现在 typecheck 报错中。
- 真实设备命令下发与受限账号显隐仍需在目标运行环境补充验收。
