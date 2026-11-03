# FEAT-0079 技术设计

- status: review
- owner: payhon
- last_updated: 2026-10-29
- related_feature: FEAT-0079
- version: v0.1.0

## 设计
扫描页以 localName、name 的顺序选取有效名称，禁止含控制字符、Unicode 替换字符的名称，保留正常 Unicode；记录当前行名称来源，避免缺失广播名称时旧 name 覆盖已确认广播名称。无法取得有效名称时保留已有有效名称，否则使用未知设备文案。

对于无名称设备，仅已解析且前缀受支持的广播 MAC 可通过原身份过滤；有名称设备沿用原服务及 MAC 检验。继续逐条处理广播，发现有效 localName 时更新列表，目标 MAC 匹配不依赖显示名称。

## 测试与兼容
验证异常名称恢复、有效值保持、空名称 MAC 匹配、无关设备过滤、扫描会话与续扫回归；真实 iOS、Android 及广播时序需分开验收。无公共 API 或数据迁移。
