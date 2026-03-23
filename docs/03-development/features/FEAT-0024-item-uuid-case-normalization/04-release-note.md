# FEAT-0024 item_uuid 大小写归一化防重复注册 - 发布说明

- status: draft
- owner: payhon
- last_updated: 2026-03-23
- related_feature: FEAT-0024

## 发布内容
- UniApp 蓝牙读取 UUID 统一输出大写十六进制字符串。
- UniApp 开通接口请求统一使用大写 `item_uuid`。
- 后端 `provision` 链路统一按大写规范值查询和写入，并兼容历史小写记录。
- 修复因 `item_uuid` 大小写不一致导致的重复自动补建设备问题。

## 上线注意事项
- 本次不包含历史重复设备清理脚本；若线上已经存在同 UUID 大小写混用的重复记录，需另行人工核对清理。
- 建议上线后优先回归蓝牙扫描添加、UUID 扫码绑定、遗留设备自动补建三条链路。
