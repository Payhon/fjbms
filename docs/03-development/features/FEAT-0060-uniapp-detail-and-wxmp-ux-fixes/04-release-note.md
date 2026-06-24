# FEAT-0060 UniApp 详情状态与小程序品牌首屏优化 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-06-18
- related_feature: FEAT-0060
- version: v0.1.0

## 1. 发布内容
- 4G BMS 设备详情顶部连接状态改为 `4G 在线` / `4G 离线`，并用颜色区分。
- 首页设备列表 4G 设备状态角标改为 `4G 在线` / `4G 离线`，不再显示 `MQTT 在线`。
- Android APP 添加设备扫码/相册识别跳转详情后，不再残留或重弹添加设备菜单。
- PACK 微信小程序冷启动时，运行配置返回前不展示富嘉默认 Logo/Banner；首页 Banner 保留布局占位，PACK 未配置专属图时继续隐藏。

## 2. 影响范围
- 影响 `fjbms-uniapp`。
- 不影响后端接口、数据库、WEB 后台、设备通信协议。

## 3. 验证建议
- 发布前执行 UniApp TypeScript 校验。
- 使用 4G 在线/离线设备各验证一次详情页顶部状态。
- Android APP 使用相册二维码进入详情页，确认添加设备菜单关闭。
- PACK 微信小程序冷启动验证首屏无默认品牌闪现。

## 4. 回滚说明
- 如出现运行态兼容问题，回滚 FEAT-0060 对 `fjbms-uniapp` 与文档看板的改动。
