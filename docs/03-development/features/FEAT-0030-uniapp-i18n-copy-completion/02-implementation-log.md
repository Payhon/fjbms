# FEAT-0030 UniApp 页面多语言文案补全 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-18
- related_feature: FEAT-0030
- version: v0.1.0

## 1. 实施记录
1. 新建 FEAT-0030 文档目录，并在项目看板登记 UniApp 条目。
2. 盘点 `fjbms-uniapp/pages/`、`components/`、`common/` 中首页、设备详情及常用页面的硬编码用户文案。
3. 按页面范围拆分并行任务，分别处理首页、设备详情、其他页面与通用模块的 i18n 补全。
4. 统一收敛到 `zh-CN.ts` / `en-US.ts`，补齐缺失 key，并保持命名空间一致。
5. 首页范围复核后确认现有实现已基本完成国际化，本轮未做无效改动。
6. 设备详情参数页将温度标签、电池类型、权限提示、更新提示从组件内硬编码迁移为统一 i18n key；设备详情仪表盘同步补齐故障计数口径与剩余时间单位文案。
7. 通用请求层与升级检测提示改造为通过 `i18n.global.t(...)` 读取字典，移除运行时中文硬编码。
8. 同步补充 `common.*` 与 `deviceDetail.params.*` 新增词条，覆盖网络异常、升级提示、电池类型和参数页提示文案。
9. 继续补齐设备添加流程的蓝牙异常提示，将 `ble-scan.vue` 中的适配器不可用报错收口到 `pages.deviceProvision.bluetoothAdapterUnavailable`。
10. 补齐 `uni_modules/fjbms-upgrade` 升级弹窗与备用 `updateUseModal()` 分支的多语言接入：
   - 将升级弹窗按钮、下载进度、安装提示、失败提示、重启提示等用户可见文案迁移到 `appUpgrade.*` 字典。
   - 新增 `common.yes` / `common.no` 与 `appUpgrade.*` 中英文词条，统一供升级弹窗和升级确认逻辑复用。
   - 同步移除升级弹窗流程中的运行时中文硬编码，避免语言切换后仍出现中文按钮或提示。

## 2. 当前状态
- 文档已建档。
- 代码改造已完成本轮范围收口。
- 已执行 `pnpm exec tsc --noEmit --pretty false`，通过。
- 待真机/小程序语言切换抽样验收，重点补看升级弹窗与升级确认链路。
