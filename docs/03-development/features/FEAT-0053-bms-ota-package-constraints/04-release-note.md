# FEAT-0053 BMS OTA 升级包约束匹配 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-05-13
- related_feature: FEAT-0053
- version: v0.1.0

## 1. 发布内容
- BMS 升级包新增 BMS 型号、批号、序列号约束。
- APP BMS OTA 检测按约束优先级返回升级包。
- BMS 升级包后台表单移除设备配置、说明、附加信息。

## 2. 影响范围
- 后台 OTA 升级包管理。
- APP 电池设备详情 OTA 检测与手动升级入口。
- 后端 APP BMS OTA 检测接口。

## 3. 升级步骤
- 发布后端、前端和 UniApp 包。
- 执行 `backend/sql/55.sql`。

## 4. 回滚步骤
- 回滚代码版本。
- 如需回滚数据库，确认没有依赖约束字段的数据后删除新增索引和字段。

## 5. 已知问题
- 历史无约束 BMS 升级包会继续作为通用包参与匹配。
