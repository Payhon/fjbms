# FEAT-0073 设备详情 UUID 复制与 4G IMEI 展示 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-08-30
- related_feature: FEAT-0073
- version: v0.1.0

## 1. 实施记录

1. 建立 FEAT-0073 功能规格、技术设计、实施日志、测试报告和发布说明，并同步项目看板。
2. 后端 APP 电池详情响应新增可空 `imei`，查询从 `device_batteries.imei` 读取，并同步 Swagger 描述和生成文件。
3. UniApp 新增纯函数标识策略，4G/双模非蓝牙链路严格显示 IMEI，IMEI 缺失显示横杠；双模蓝牙与纯蓝牙继续显示格式化 MAC。
4. 设备详情仪表盘页新增完整 UUID 卡片，UUID 缺失时显示横杠并禁用复制；有效 UUID 点击后写入剪贴板并显示中英文成功/失败反馈。
5. 通用仪表组件将 `footerMacText` 收敛为 `footerIdentifierText`，同步 App/H5 插槽和微信小程序 Canvas 绘制及重绘监听。
6. 未修改 `useBatteryDetail` 的连接、轮询、数据仲裁、OTA 或设备绑定逻辑；详情页既有未提交 4G 在线宽限改动保持原状。
7. 2026-08-30 将包含 IMEI 详情字段的 Linux amd64 后端二进制部署至生产环境，仅替换 `/www/fjia/fjbms/backend/fjbms` 并重启 `fjbms-backend`，未同步配置或 SQL。
8. 部署前备份旧二进制至 `/www/fjia/backups/fjbms/backend/backend_20260830_175322_pre_feat0073.bin`，旧二进制 SHA-256 为 `364c1efa5067571d5be3d3aa560b88ea9e3bec0dee96621f8233e7956f589575`。

## 2. 验证记录

- `cd backend && go test ./internal/model ./internal/service ./internal/api ./router/apps -count=1`：2026-08-30 通过；仅有既有 macOS `IOMasterPort` 弃用警告。
- `cd backend && swag init`：2026-08-30 通过；生成文件仅增加详情描述和 IMEI schema。
- `cd fjbms-uniapp && pnpm dlx tsx pages/device-battery/device-detail-identifier.test.ts`：2026-08-30 通过。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`：2026-08-30 通过。
- 使用 `frontend` 已安装的 `@vue/compiler-sfc` 解析并编译详情页、仪表盘页和仪表组件：2026-08-30 通过。
- HBuilderX 5.24 微信小程序编译：2026-08-30 通过；仅提示未配置 uniCloud 本地调试空间，不影响项目编译。
- 根仓、`backend`、`fjbms-uniapp` 差异检查：2026-08-30 通过。
- 生产后端二进制 SHA-256：`32f46978df515c41c05ea91326587d7a7c9a6da00cc92b09ce1ca3147403b981`，与本地构建一致；`fjbms-backend` 为 `active/running`，`http://127.0.0.1:9999/health` 返回 HTTP 200。
- 生产运行中 Swagger 已包含 `AppBatteryDetailResp.imei` 及详情接口 IMEI 描述。
- 生产数据库确认 `item_uuid=360111611350535934373730300A377B` 对应 `bms_comm_type=2`、`imei=862415070098188`。

## 3. 待现场验证

- 375px 微信小程序、Android、iOS 设备详情实际布局与剪贴板行为。
- 真实 4G、双模和纯蓝牙设备标识切换。
- 重新进入生产移动端详情页，确认新的认证详情请求返回 IMEI 并替换原 `IMEI: -`。
