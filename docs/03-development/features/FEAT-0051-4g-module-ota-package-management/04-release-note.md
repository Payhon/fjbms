# FEAT-0051 4G模块 OTA 升级包管理 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-05-07
- related_feature: FEAT-0051
- version: v0.1.0

## 发布内容
- 后台 `升级包管理` 新增 `4G模块升级包`。
- 升级包列表新增固件 URL 展示与复制。
- 新增 4G 模块公开升级检查接口。

## 数据库变更
- 执行 `backend/sql/54.sql`。
- `ota_upgrade_packages` 新增或补齐 `device_kind`、`is_latest` 字段。

## 回滚说明
- 回滚代码后，如需回滚数据库字段，需先确认没有 4G 模块升级包生产数据。
