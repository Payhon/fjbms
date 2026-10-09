# FEAT-0013 移动端设备添加分流、首页视图切换与筛选增强 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-09-28
- related_feature: FEAT-0013
- version: v0.1.3

## 1. 测试范围
- 终端用户添加设备、绑定激活与首页筛选。
- 机构用户添加设备、首页模式切换与首页筛选。
- 激活日志与激活统计口径修正。
- 大列表场景下首页分页与服务端筛选可用性。
- OpenHarmony 微信长按设备卡片后的管理事件负载与解绑 `device_id` 校验。
- 终端用户自定义名称的绑定范围、首页/详情一致性、解绑重绑恢复原名及旧版改名请求兼容。
- 解绑/移除后内存列表与微信扫码快照一致性、重复添加及原有扫码返回规则。

## 2. 已执行验证
- [x] 后端编译级验证：
  - [x] `cd backend && go test ./internal/service -run TestDoesNotExist`
  - 结果：通过，确认 FEAT-0013 相关服务层代码可编译。
- [x] 绑定名称服务层回归：
  - [x] `cd backend && go test ./internal/service -run 'TestBoundDeviceNameResetsAfterUnbind|TestGetBatteryDetailForAppIncludesImei|TestAppUnbindClearsBleMacWhenNoAppAssociationsRemain' -count=1`
  - 结果：通过；用户 A 改名后用户 B 仍显示原名，绑定业务备注不受影响，无绑定用户改名被拒，A 解绑再绑定后首页和详情恢复原名。
  - [x] `cd backend && go test ./internal/service ./internal/api ./router/apps`
  - 结果：服务层、接口层通过，路由包无测试文件。
- [x] UniApp 类型检查：
  - [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过。
- [x] 首页设备动作 ID 策略测试：
  - [x] `cd fjbms-uniapp && pnpm dlx tsx common/home-device-action.test.ts`
  - 结果：通过；有效 ID 正常返回，原生 `longpress` 事件对象以及空值、`undefined`、`null`、`[object Object]` 均被拒绝。
- [x] HBuilderX 微信小程序编译：
  - [x] `/Applications/HBuilderX.app/Contents/MacOS/cli launch mp-weixin --project /Users/payhon/work2025/project/fjbms/fjbms-uniapp --compile true --continue-on-error false`
  - 结果：编译成功；产物确认卡片根节点为 `catchlongpress`、父页面为 `bindmanage`，不再存在父子同名 `bindlongpress`。编译过程仍提示既有 uniCloud 本地服务空间未配置及 BLE UA 检测警告，与本次事件修复无关。
- [ ] 后端单元/集成测试：
  - [ ] `END_USER` 添加设备后写绑定关系并激活。
  - [ ] `ORG_USER` 添加设备后仅写添加记录，不激活。
  - [ ] `view_mode=self_bound` 查询正确。
  - [ ] `view_mode=org_added` 查询正确。
  - [ ] `view_mode=end_user_bound` 且机构范围过滤正确。
  - [ ] 激活日志不包含机构用户“仅添加”记录。
- [ ] 手工验收：
  - [ ] 我的页切换图标仅机构用户显示。
  - [ ] 首页模式标签与当前数据源一致。
  - [ ] 终端用户筛选：名称/序列号/MAC 地址。
  - [ ] 机构用户“我添加的设备”筛选：添加日期/序列号/MAC 地址。
  - [ ] 机构用户“终端用户绑定设备”筛选：名称/序列号/MAC 地址。
  - [ ] 机构用户“终端用户绑定设备”模式下无解绑/移除操作。
  - [ ] OpenHarmony 微信真机长按设备卡片并解绑，确认请求携带真实 UUID 且返回 `code=200`。
  - [x] 在目标数据库确认 `device_user_bindings.custom_name` 迁移成功；历史受影响设备的原始名称仍待可信来源核对。
  - [ ] 微信小程序、Android、iOS 实际设备执行“改名 → 解绑 → 再添加”，确认首页/详情显示原名及另一账号名称不变。

## 3. 执行结果与阻塞
- `cd backend && go test ./...`
  - 结果：未能全量通过。
  - 阻塞原因：`backend/test/pg_test.go` 依赖本地数据库环境与 `run_env=localdev` 配置，当前环境报“未知环境”并在测试初始化阶段 panic。
  - 结论：该失败属于既有测试环境依赖，当前不能据此判定 FEAT-0013 功能实现异常。

## 4. 缺陷与风险
- UniApp 当前仅执行 `tsc`，仓库未接入 `vue-tsc`，因此 SFC 模板层面的静态校验覆盖有限，仍需真机或 HBuilderX 编译验证。
- 需重点关注大列表性能、BLE 扫描页已添加设备过滤策略以及模式切换后的缓存一致性。
- OpenHarmony 微信的代码与编译产物验证已完成，但尚未在用户真机上执行修复后解绑，因此真实设备闭环仍待发布版本复测。
- 历史已被移动端写入 `devices.name` 的自定义名称，无法凭现有字段自动还原原名；本次代码回归不代表这些历史记录已完成数据修复。
- 生产库发布前只读核对：2026-09-24 共 586 条绑定，`remark` 非空 0 条；但后台激活流程可向该列写入业务备注，因此新增独立 `custom_name` 列。
- 2026-09-24 生产发布：`backend/sql/66.sql` 执行成功；生产列类型 `varchar(255)`、可空，发布后 587 条绑定的 `custom_name` 均为空，587 条绑定可通过新名称表达式读出名称。生产二进制 SHA-256 `a27e66e1afc2baec59f0c9dd441b03c70dc5df10c422f678358ae2881238a664` 与本地一致，`fjbms-backend` 保持 `active`，`/health` 返回 200，匿名访问设备列表返回 401，发布后 `NRestarts=0`、服务日志无 `panic/fatal/error` 命中。
- 生产真实账号/设备的“改名 → 解绑 → 再添加”尚未执行；现有生产日志可确认至少两台设备的全局名称已被旧版改名覆盖，但缺少可信的更名前名称，历史数据未自动修改。

## 5. 结论
- 当前处于开发进行中，编译级验证已通过，完整联调与业务验收待数据库环境和真机验证完成后回填。

## 6. 2026-09-28 解绑后重复扫码添加修复
- [x] `cd fjbms-uniapp && node store/bound-devices-snapshot.test.js`
  - 使用真实 Pinia，执行实际 store、首页 `confirmUnbind` / `confirmRemove` 和微信自定义 TabBar 扫码 handler；列表 API、弹窗与微信原生 API 使用隔离模拟。
  - 终端用户与机构用户各三轮“添加刷新 → 解绑/移除 → 再次扫码”通过：内存列表和快照只删除目标，MAC 进入 BMS 添加扫描页，UUID 进入绑定页，其他设备仍直达详情。
  - 接口失败、抛出异常、取消确认均保留列表和快照；store 清空时快照也清空。
  - 负向对照仅在内存中去掉新增同步调用，测试在首次解绑后以“快照仍含 device-A”失败，确认回归检查能捕获原缺陷。
- [x] 原扫码行为回归：`node pages/device-provision/ble-scan-auto-start.test.js`、`node common/device-provision/scan-routing.test.js`、`node common/device-provision/ble-search-entry-route.test.js` 均通过，保留同一次扫码只自动连接一次、返回扫描页停止扫描及新扫码入口行为。
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`：通过。
- [x] `/Applications/HBuilderX.app/Contents/MacOS/cli launch mp-weixin --project /Users/payhon/work2025/project/fjbms/fjbms-uniapp --compile true --continue-on-error false`：HBuilderX 5.26 编译成功；`unpackage/dist/dev/mp-weixin/store/bound-devices.js` 的移除动作包含快照同步。仍提示既有 uniCloud 服务空间未配置，未阻止编译。
- [x] 新测试脚本语法检查、根仓及 UniApp `git diff --check`：通过。
- [ ] 微信真机执行“扫码添加 → 详情断开 → 返回首页 → 解绑 → 再次扫码添加 → BLE 连接成功”，连续三轮；同时复测不解绑的扫码直达。
- [ ] Android/iOS App 重复添加/解绑和机构用户移除冒烟。
- 结论：本地缓存与扫码路由回归、类型与微信编译已通过；模拟检查不代表真实 BLE 连接验收。未提交、推送或发布，功能仍为 `in_progress`。


## 2026-10-09 Git 交付前复核

- `go test ./internal/service ./internal/api ./router/apps` 通过，包含绑定名称隔离及解绑重绑回归；修改的 Go 文件均通过 gofmt 检查。
- `node store/bound-devices-snapshot.test.js` 及原扫码路由/生命周期回归通过；UniApp TypeScript 和受影响页面两平台分支 SFC 编译通过。
- 本轮按用户授权拆分 Git 提交并推送；未重新打包/发布移动端、部署服务或操作数据库，真机验收和功能状态保持原记录。
