# FEAT-0068 移动端质保资料填写引导 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-07-10
- related_feature: FEAT-0068
- version: v0.1.0

## 2026-07-10
1. 扩展 App 质保 profile，按用户主动保存的联系人记录计算 `warranty_profile_completed` 和 `warranty_profile_reminder_needed`。
2. 扩展设备开通绑定响应 `newly_bound`，复用绑定事务的当前用户关联检查。
3. 新增 UniApp 质保提醒 Pinia store，统一同步原生 TabBar 和微信自定义 TabBar 红点，并在 App 与首页生命周期静默刷新。
4. 在 UUID 绑定页、蓝牙开通向导接入可跳过的质保资料引导；立即填写进入自动编辑态资料页。
5. 我的页质保入口增加红点，质保资料页增加说明提示条；保存成功后即时清除提醒。
6. 补齐中英文文案、后端定向测试、FEAT 文档和看板记录。
7. 根据生产验收反馈，移除 App profile 对账号姓名、手机号的联系人回填；新增 `warranty_profile_exists`，质保页在无表记录时展示“个人质保信息未填写”和立即填写入口。
