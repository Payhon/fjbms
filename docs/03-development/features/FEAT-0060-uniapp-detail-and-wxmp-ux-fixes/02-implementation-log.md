# FEAT-0060 UniApp 详情状态与小程序品牌首屏优化 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-06-18
- related_feature: FEAT-0060
- version: v0.1.0

## 1. 实施记录
1. 设备详情页新增 4G 设备状态分支，按 `is_online` 展示 `4G 在线` / `4G 离线`，并补充中英文文案与状态样式。
2. 首页设备卡片新增 4G 状态分支，按 `isOnline` 展示 `4G 在线` / `4G 离线`，不再显示 `MQTT 在线`。
3. 添加设备共享入口新增扫码流程 guard，覆盖扫码进行中、扫码取消、无效码、成功跳转后的 ActionSheet 抑制。
4. 中间 Tab 页在共享入口返回未处理时主动切回上一次 Tab，避免 Android 相册扫码回跳后停留占位页并重弹菜单。
5. 首页 Banner 与登录 Logo 在微信小程序端初始为空，运行配置返回后按 PACK/非 PACK 策略展示。
6. 补充首页 Banner 容器固定 421rpx 高度，占位保留但不展示默认品牌图，避免运行配置返回前页面布局塌陷。
7. 新增 FEAT-0060 文档并同步项目看板。

## 2. 当前状态
- 代码改造已完成。
- UniApp TypeScript 校验和空白检查已通过，结果记录在 `03-test-report.md`。
- Android 真机与微信小程序真机/开发者工具回归仍需在目标运行环境执行。
