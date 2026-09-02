# FEAT-0073 设备详情 UUID 复制与 4G IMEI 展示 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-08-30
- related_feature: FEAT-0073
- version: v0.1.0

## 1. 测试范围

- APP 电池详情 IMEI 响应字段。
- UUID 完整展示、空值与剪贴板交互。
- 4G/双模/蓝牙仪表标识选择。
- App/H5 与微信小程序两条仪表文本渲染路径。

## 2. 测试环境

- 本地 Go、UniApp TypeScript 与 Vue SFC 编译环境。
- 微信开发者工具和真实 Android/iOS 设备待验证。

## 3. 用例结果

1. 后端详情接口与相关包
   - 命令：`cd backend && go test ./internal/model ./internal/service ./internal/api ./router/apps -count=1`
   - 结果：通过；SQLite 用例确认详情响应返回数据库中的 IMEI，仅有既有 macOS `IOMasterPort` 弃用警告。
2. Swagger
   - 命令：`cd backend && swag init`
   - 结果：通过；详情接口描述包含 `imei`，`AppBatteryDetailResp` schema 新增 IMEI 字段。
3. UniApp 标识策略
   - 命令：`cd fjbms-uniapp && pnpm dlx tsx pages/device-battery/device-detail-identifier.test.ts`
   - 结果：通过；覆盖纯 4G、双模离线、双模蓝牙、纯蓝牙、IMEI 缺失不回退 MAC、MAC 格式化和 UUID 空值/去空格。
4. TypeScript 与 Vue SFC
   - 命令：`cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
   - 结果：通过。
   - 使用 `frontend` 本地 `@vue/compiler-sfc` 编译 `detail.vue`、`dashboard-tab.vue`、`dashboard-gauge.vue`：通过。
5. 微信小程序编译
   - 命令：`HBuilderX cli launch mp-weixin --project <fjbms-uniapp绝对路径> --compile true --continue-on-error false`
   - 结果：HBuilderX 5.24 编译成功；产物包含 UUID 卡片、复制回调、IMEI 策略和通用仪表标识属性。uniCloud 本地调试空间缺失提示不影响本项目编译。
6. 差异检查
   - 根仓、`backend`、`fjbms-uniapp` 的 `git diff --check`：通过。
7. 生产后端部署
   - 结果：2026-08-30 17:53:39 CST 完成生产二进制替换并重启 `fjbms-backend`，服务保持 `active/running`。
   - 校验：线上二进制 SHA-256 为 `32f46978df515c41c05ea91326587d7a7c9a6da00cc92b09ce1ca3147403b981`，与本地构建一致；服务本机 `/health` 返回 HTTP 200。
   - 接口契约：运行中 Swagger 已出现详情响应 `imei` 字段及 `device_batteries.imei` 描述。
   - 数据：生产库中 `360111611350535934373730300A377B` 对应 IMEI 为 `862415070098188`，通讯类型为纯 4G（`bms_comm_type=2`）。
   - 回滚备份：`/www/fjia/backups/fjbms/backend/backend_20260830_175322_pre_feat0073.bin`。
8. 全量后端测试补充
   - `go test ./... -count=1` 在既有环境依赖用例失败：`initialize/test` 未初始化告警缓存，`test/pg_test.go` 缺少 `run_env` 数据库环境；失败文件不属于 FEAT-0073 差异，目标相关包测试通过。

## 4. 缺陷与风险

- 静态检查和微信编译不能证明真实设备剪贴板授权、Canvas 字体宽度和不同系统字号缩放下的最终效果。
- 375px 微信小程序、Android/iOS 真机和真实 4G/双模/蓝牙设备验收待执行。
- 生产认证详情接口尚需由移动端重新进入页面触发并确认最终界面；当前已完成线上二进制、健康检查、Swagger 契约和生产数据四项验证。

## 5. 结论

- 代码、自动化、微信小程序编译和生产后端部署验证通过，状态保持 `review`。
- 真机和真实设备验收完成前不标记 `done`。
