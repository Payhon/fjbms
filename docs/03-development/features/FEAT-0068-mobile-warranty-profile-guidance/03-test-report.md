# FEAT-0068 移动端质保资料填写引导 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-07-10
- related_feature: FEAT-0068
- version: v0.1.0

## 自动化结果
| 类型 | 结果 | 说明 |
| --- | --- | --- |
| 后端定向测试 | 通过 | `go test ./internal/service -run 'Test(AppWarrantyProfile\|BindEndUserDeviceTx\|ApplyBatteryWarrantyActivationTx)' -count=1` |
| 后端路由与 API 编译级测试 | 通过 | `go test ./internal/api ./router/apps ./internal/service -run 'Test(AppWarrantyProfile\|BindEndUserDeviceTx\|ApplyBatteryWarrantyActivationTx)' -count=1` |
| UniApp TypeScript 检查 | 通过 | `pnpm exec tsc -p tsconfig.json --noEmit --skipLibCheck` |
| 微信自定义 TabBar 语法 | 通过 | `node --check custom-tab-bar/index.js` |
| 空白检查 | 通过 | 根仓、backend、fjbms-uniapp 均执行 `git diff --check` |

## 后端覆盖场景
1. 无绑定设备的完整质保资料不需要提醒。
2. 仅账号姓名、手机号回填不视为用户已完成质保资料。
3. 已绑定设备但只填写姓名或电话时仍需提醒。
4. 已绑定设备且姓名、电话均由用户保存时完成资料并关闭提醒。
5. 已绑定当前用户重复调用绑定事务返回 `newly_bound=false`；新增关联返回 `true`。
6. 删除 `user_warranty_infos` 记录后，profile 返回的联系人字段为空且 `warranty_profile_exists=false`，不会回填账号姓名、手机号。

## 待运行态回归
1. UUID 扫码绑定和蓝牙开通向导各验证一次“立即填写”和“以后再说”。
2. 微信小程序、iOS、Android 的“我的”Tab 红点、菜单红点和质保页顶部提示一致。
3. 保存完整资料后所有提示立即消失；网络失败或重复绑定不阻断原详情跳转。
