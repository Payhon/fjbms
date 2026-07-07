# FEAT-0062 用户质保信息与 PACK 质保卡片开关 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-07-01
- related_feature: FEAT-0062
- version: v0.1.0

## 1. 实施记录
1. 新增 `backend/sql/60.sql`，包含用户质保信息表、`device_batteries` 质保字段、PACK 小程序配置开关和后台页面元素权限。
2. 后端新增 `UserWarrantyInfo` 服务和 API，支持移动端个人质保 profile、后台电池质保查询与编辑。
3. 后端扩展 PACK 小程序配置接口和运行时接口，增加 `warranty_cards_enabled`，并收紧 PACK 厂账号只能配置自己组织。
4. 后端在用户绑定、开通向导绑定、电池生命周期激活链路中补充质保起始日期和到期日计算。
5. Web 后台 PACK 小程序配置弹窗新增“启用质保卡片”开关。
6. Web 后台电池详情 BMS 模式新增“质保”Tab，展示电池质保字段、绑定用户和人工编辑弹窗。
7. UniApp 新增 `pages/my/warranty/index` 质保信息页和 “我的”页终端用户菜单入口。
8. UniApp 新增 `service/user-warranty.ts`，请求时携带当前运行时 AppID。
9. 补齐 Web 和 UniApp 中英文文案、页面标题和文档五件套。
10. 根据移动端截图反馈优化质保信息页：个人质保信息默认只读，右上角铅笔按钮进入编辑态后才显示保存按钮；关联电池改为拟物化质保凭证卡片视觉，增加浅色材质、金色细节、分区信息块和层次阴影；二次调整卡片排版，型号改为编号上方右侧小灰字，质保时长改为编号下方小字，底部信息块仅保留激活日期和质保到期。
11. 使用 imagegen 生成 `icon-warranty@2x.png`，替换移动端“我的”页质保信息入口图标，避免继续复用“帮助与反馈”图标。

## 2. 当前状态
- 后端、Web、UniApp 代码改造已完成。
- 已补充后端定向单测。
- 本地静态检查与类型检查结果见 `03-test-report.md`。
- PACK 小程序真机展示、PACK_FACTORY 实际后台账号权限和后台页面人工验收仍需目标环境补充。
