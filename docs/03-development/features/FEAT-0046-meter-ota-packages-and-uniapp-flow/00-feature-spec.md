# FEAT-0046 仪表 OTA 升级包与 UniApp 独立升级链路 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-04-21
- related_feature: FEAT-0046
- version: v0.1.0

## 1. 背景与目标
- 当前 OTA 升级包管理与 UniApp 升级入口均围绕 BMS 设备设计，蓝牙仪表虽然走 Boot OTA 协议，但缺少独立的升级包管理和手动选包升级链路。
- 本次目标：
  1. 在 `ota_upgrade_packages` 中引入 `device_kind`，支持同表管理 BMS / 仪表升级包。
  2. 后台升级包管理页改为双 TAB，仪表升级包使用精简字段。
  3. UniApp 在蓝牙仪表详情页隐藏原 BMS OTA 检测入口，改为仪表专用“选包后升级”流程。

## 2. 范围
### In Scope
- `backend/sql/51.sql` 为 OTA 升级包增加 `device_kind` 字段。
- `/api/v1/ota/package` 支持 `device_kind` 读写与分页过滤。
- 新增 `/api/v1/app/battery/ota/meter-packages` 返回仪表升级包全量列表。
- 后台 `升级包管理` 页面改为 `BMS 升级包 / 仪表升级包` 双 TAB。
- UniApp 设备详情参数页新增“仪表升级”卡片，仪表升级走手动选包 + `0xFC` Boot OTA。

### Out of Scope
- 不改 OTA 分包、CRC、Boot 帧格式。
- 不对仪表升级包做型号匹配或版本比较。
- 不新增第二张仪表升级包表。

## 3. 验收标准
1. `ota_upgrade_packages.device_kind` 可区分 BMS(`1`) 与仪表(`2`) 包。
2. 后台升级包管理页可按 TAB 分别管理 BMS 与仪表包；仪表表单仅包含名称、文件、说明。
3. `/api/v1/app/battery/ota/meter-packages` 仅返回当前租户仪表升级包的 `id/name/description/package_url`。
4. UniApp 蓝牙仪表详情页隐藏旧 OTA Cell 与红点，显示“仪表升级”卡片。
5. 用户选择仪表固件并确认后，升级直接下载所选固件并按 `0xFC` 目标地址执行。
6. 蓝牙已连接但仪表尚未与后端 BMS 建立透传时，设备详情状态区可为空，前端不应无限重试读取状态；该场景仍须允许仪表升级。

## 4. 风险与约束
- 仪表包与 BMS 包同表存储，历史 BMS 字段约束仍存在，因此仪表包需在服务层自动填充兼容值。
- 仪表升级包列表按租户全量返回，若同租户仪表固件较多，移动端选择体验依赖命名规范。

## 5. 回滚方案
- 回滚 `device_kind` 相关服务与前端调用。
- UniApp 回滚至现有 BMS OTA 入口逻辑，取消仪表升级卡片。
- 文档与看板状态同步回退。
