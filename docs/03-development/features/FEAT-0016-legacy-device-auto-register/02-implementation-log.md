# FEAT-0016 遗留 BMS 设备 UUID 自动补建 - 实现日志

- status: in_progress
- owner: payhon
- last_updated: 2026-03-17
- related_feature: FEAT-0016
- version: v0.1.0

## 2026-03-17
- 完成功能规格与技术设计，确定采用“`info` 只读、`bind` 懒注册”的实现边界。
- 确认现有链路入口：
  - 后端：`backend/internal/service/device_provision.go`
  - UniApp：`fjbms-uniapp/pages/device-provision/provision-wizard.vue`
- 确认自动补建只创建最小占位记录，不在首版推断 `product_id/device_config_id`。
- 已实现后端：
  - `provision/info` 返回 `exists/can_auto_register/auto_register_reason`
  - `provision/bind` 在查不到设备时按配置开关自动补建 `devices + device_batteries`
  - end-user 绑定路径改为在 `device_provision` 内部事务中完成激活与绑定
  - org-user 添加路径改为事务内 upsert `app_device_added_records`
  - 新增配置 `bms.provision.allow_legacy_auto_register`
- 已实现 UniApp：
  - 开通向导识别 `exists=false && can_auto_register=true`
  - 增加“遗留设备自动注册后继续绑定”的提示文案
