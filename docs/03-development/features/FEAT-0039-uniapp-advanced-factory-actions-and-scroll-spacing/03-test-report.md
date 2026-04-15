# FEAT-0039 UniApp 设备详情高级参数出厂命令补齐与底部遮挡修复 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-15
- related_feature: FEAT-0039
- version: v0.1.0

## 1. 已执行验证
- [x] `cd backend && go test ./...`
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`
- [ ] 真机 / HBuilderX 手工验收

## 2. 验证结果
- `cd backend && go test ./...`
  - 结果：失败。
  - 备注：存在与本次需求无关的仓库既有测试失败，主要包括：
    - `project/initialize/test.TestSetDevice` 空指针崩溃
    - `project/test.TestDatebase` 缺少本地环境配置后触发空指针崩溃
  - 备注：`project/internal/service` 包测试通过，本次修改涉及的 `backend/internal/service/device_param_permission_tree.go` 未引入新增编译错误。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过。

## 3. 待补充手工验收
- [ ] 设备详情 > 设置 > 高级参数 > 出厂配置中可看到“擦除当前参数”
- [ ] 可看到“擦除历史记录”
- [ ] 可看到“擦除循环次数”
- [ ] 可看到“清除保护状态”
- [ ] 可看到“复位保护板”
- [ ] 点击上述命令时仍出现确认弹窗，并走命令发送成功/失败提示
- [ ] 高级参数弹层滚动到底部时，末尾工厂命令不会被底部 Tab 挡住
- [ ] 最后一项命令可以稳定点击
- [ ] 后台设备参数权限树可看到新增工厂命令权限项
