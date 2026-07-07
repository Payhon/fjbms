# FEAT-0064 移动端与 Web BMS 展示修正 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-07-07
- related_feature: FEAT-0064
- version: v0.1.0

## 1. 发布内容
- PACK 微信小程序未配置专属图片时，不再回退显示富嘉默认 Banner/Logo。
- 移动端 BMS 保护状态值统一显示为 `ON/OFF`。
- Web BMS 面板电芯电压值改为横向显示。

## 2. 影响范围
- `fjbms-uniapp` 首页、登录页、设备详情 BMS 保护状态。
- `frontend` 电池详情 BMS 面板电芯 TAB。
- 不影响后端接口、数据库、权限和设备通信协议。

## 3. 发布前检查
- UniApp TypeScript 校验通过。
- Web TypeScript 校验和 targeted ESLint 通过。
- 文档和看板空白检查通过。
- 小程序和 Web 运行态完成手工回归。

## 4. 回滚说明
- 回滚 UniApp runtime 默认品牌图 helper、首页/登录页调用和保护状态文案改动。
- 回滚 Web BMS 面板电芯电压 CSS 改动。
