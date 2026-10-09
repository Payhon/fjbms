# FEAT-0030 UniApp 页面多语言文案补全 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-09-24
- related_feature: FEAT-0030
- version: v0.1.0

## 1. 测试范围
- 首页及首页相关组件多语言切换。
- 设备详情页及子组件多语言切换。
- “我的”、告警、通知详情、机构设备页与通用提示文案多语言切换。

## 2. 已执行
1. 静态校验
   - 命令：`cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
   - 结果：通过。
2. 页面与模块抽查
   - 首页范围：复核 `pages/home/home.vue`、`components/home/device-card.vue`、`components/customNav/customNav.vue`，确认当前用户可见文案已基本通过 `$t/t` 输出，本轮无新增代码修改。
   - 设备详情范围：确认 `pages/device-battery/components/params-tab.vue` 中温度标签、电池类型、更新提示、无权限提示已切换为统一 i18n key；`dashboard-tab.vue` 的剩余时间单位已走 `deviceDetail.unit.minutes`。
   - 通用模块范围：确认 `common/request.ts`、`common/util.ts` 中 token 失效、请求失败、上传失败、网络断开、升级提示等运行时文案已切换为字典读取。
   - 设备添加流程：确认 `pages/device-provision/ble-scan.vue`、`pages/device-provision/provision-wizard.vue`、`pages/device-provision/uuid-bind.vue` 与 `common/composables/useAddDeviceActionSheet.ts` 的可见文案均已收口到 `pages.deviceProvision.*`，并补齐蓝牙适配器不可用提示。
   - 升级弹窗范围：确认 `uni_modules/fjbms-upgrade/pages/upgrade-popup.vue` 与 `uni_modules/fjbms-upgrade/utils/check-update.ts` 的按钮、toast、modal、通知进度标题等可见文案已切换为 `appUpgrade.*` / `common.yes` / `common.no`。
3. 2026-09-24 原生确认弹窗英文修复
   - `pnpm exec tsc -p tsconfig.json --noEmit --pretty false`：通过。
   - 静态读取中英文字典：8 个原生弹窗短按钮词条在两种语言中均不超过 4 个字符。
   - 受影响的 5 个 Vue 页面 SFC 解析通过；设置页 `script setup` 编译检查通过。
   - 微信小程序更新控制器现有测试通过；`git diff --check` 通过。
4. 2026-09-24 同类调用复核
   - 扫描 `pages/`、`common/`、`uni_modules/` 的全部 `showModal` 调用；业务代码和实际接入的升级模块中，23 处显式按钮词条在中英文下共 46 个值均不超过 4 个字符。
   - `uview-next` 定位弹窗的 3 处固定确认文案均为 4 个汉字；`uni-forms` 校验弹窗使用原生默认按钮，无超长自定义文案。
   - `fjbms-upgrade/utils/check-update.ts` 中较长的升级按钮仅位于 `#ifdef APP` 的可选路径；`uni-upgrade-center-app` 未被项目入口或路由引用。微信小程序可达路径未发现新的按钮文案超限项。

## 3. 风险备注
- 仓库当前缺少覆盖 UniApp UI 的自动化测试，本次仍以静态校验与人工抽样为主。
- 设备详情与“我的”等页面仍建议在中文/英文语言下各做一次真机或小程序抽样，重点关注 toast、升级弹窗与参数页电池类型选择器。
- 升级弹窗仍需在中文/英文运行态各触发一次，确认按钮、下载中提示、安装确认与失败提示均随语言切换生效。
- 设备添加流程建议再重点抽测扫码模式和蓝牙扫描失败兜底，确认错误文案没有 key 原样透出。
- 微信小程序真机尚未验收：需在英文下分别点击设置页退出登录、账号注销并确认弹窗出现；取消不执行操作，确认后分别执行退出或原有注销流程。中文回归及其他原生弹窗抽测仍需在新包中完成。


## 2026-10-09 Git 交付前复核

- 中英文 8 个原生弹窗短按钮词条（共 16 个值）均通过不超过 4 字符的断言；更新控制器回归通过。
- UniApp TypeScript、全部 8 个修改页面在微信小程序和 App 分支的 SFC 编译通过。
- 本轮按用户授权拆分 Git 提交并推送；未重新打包/发布移动端、部署服务或操作数据库，真机验收和功能状态保持原记录。
