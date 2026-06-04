# FEAT-0058 Web 后台 BMS 模块多语言补齐

- owner：payhon
- status：review
- module：`frontend`
- created_at：2026-06-04
- updated_at：2026-06-04

## 背景

英文环境下，Web 后台 BMS 设备详情仍有中文文案残留：左侧菜单显示 `route.bms_*` 权限/路由 key，设备详情 BMS 模式的外层 Tab、BMS 面板 Tab、参数设置表格、基础信息和操作记录仍直接渲染中文。

根因：

- `frontend/src/locales/langs/en-us/route.json` 缺少 BMS 路由 key。
- 设备详情 BMS 专用组件存在硬编码中文。
- 参数 label 查不到 i18n 时回退 `param-registry.ts` 的中文协议 label。
- 功能配置和工厂命令文案来自中文常量。

## 目标

1. 英文环境下，BMS 左侧菜单、面包屑和页签不再显示 `route.bms_*`。
2. 英文环境下，设备详情 BMS 模式外层 Tab、BMS 面板、参数设置、基础信息、操作记录不再出现用户可见中文。
3. BMS 参数 label 优先使用 `bms.param.<KEY>` 中英文翻译，缺失时才回退协议注册表。
4. 不修改后端接口、权限 key、路由 name、协议寄存器或设备通信逻辑。

## 范围

### Included

- `frontend/src/locales/langs/en-us/route.json`
- `frontend/src/locales/langs/{zh-cn,en-us}/bms.json`
- `frontend/src/views/bms/dashboard/index.vue`
- `frontend/src/views/device/details/index.vue`
- `frontend/src/views/device/details/modules/bms-panel/index.vue`
- `frontend/src/views/device/details/modules/battery-basic-info.vue`
- `frontend/src/views/device/details/modules/battery-operation-log.vue`

### Remaining

- `frontend/src/views/bms/**` 中电池列表、组织、用户、经销商、维保、OTA 等页面仍存在较多既有中文硬编码，需要后续逐页迁移并验证。

### Excluded

- 后端接口和权限树结构。
- 移动端 FEAT-0057 代码。
- 非 BMS 模块的后台页面。

## 验收

- `route.bms*` / `perm.bms*` 英文缺失数为 0。
- `bms.param.<KEY>` 覆盖 Web 协议注册表全部 147 个参数 key。
- BMS Dashboard 与设备详情 BMS 模式相关组件仅允许注释保留中文，不允许用户可见中文硬编码。
- `pnpm typecheck` 通过。
