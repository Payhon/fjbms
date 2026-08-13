# FEAT-0072 微信小程序版本更新检测 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-08-13
- related_feature: FEAT-0072
- version: v0.1.0

## 1. 测试范围

- 更新监听器幂等注册。
- 前台和后台更新就绪处理。
- 用户确认应用更新。
- 无更新、下载失败和非微信小程序兼容边界。

## 2. 测试环境

- 本地 UniApp TypeScript 与 Vue SFC 编译环境。
- 微信开发者工具/真机运行时待验证。

## 3. 用例结果

1. TypeScript 检查
   - 命令：`cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
   - 结果：2026-08-13 通过。
2. 更新状态机断言
   - 命令：`cd fjbms-uniapp && pnpm dlx tsx common/wx-miniapp-update-controller.test.ts`
   - 覆盖：重复启动只注册一次、无更新不提示、前台更新就绪、后台就绪后前台提示、不可取消、确认只应用一次、下载失败不应用、就绪后又失败的竞态保护。
   - 结果：2026-08-13 通过。
3. 应用入口 SFC 解析
   - 方法：使用本地 `@vue/compiler-sfc` 解析并编译 `App.vue` 脚本块。
   - 结果：2026-08-13 通过。
4. 差异检查
   - 根目录与 `fjbms-uniapp` 的 `git diff --check`：2026-08-13 通过。

## 4. 缺陷与风险

- 本地模拟只能验证状态机和 API 调用，不能证明微信公众平台已向指定用户下发新版本。

## 5. 结论

- 代码和自动化验证通过，状态进入 `review`；实际发布更新验收前不标记 `done`。
