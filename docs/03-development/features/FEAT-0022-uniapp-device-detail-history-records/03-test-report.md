# FEAT-0022 UniApp 设备详情页历史记录功能 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-03-29
- related_feature: FEAT-0022
- version: v0.1.0

## 1. 已执行验证
- [x] `cd backend && go test ./internal/service/...`
- [x] `cd backend && go test ./internal/api/...`
- [x] `cd frontend && pnpm exec vue-tsc --noEmit --skipLibCheck`
- [x] `cd frontend && pnpm exec vue-tsc --noEmit --skipLibCheck 2>&1 | rg "src/views/management/permission/index.vue|src/service/api/org-type-permissions.ts"`
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`
- [x] 协议样例字段解析验证
- [ ] 真机 / HBuilderX 手工验收

## 2. 验证结果
- `cd backend && go test ./internal/service/...`
  - 结果：通过。
- `cd backend && go test ./internal/api/...`
  - 结果：通过（含 `gopsutil/disk` 的 macOS `IOMasterPort` 弃用编译告警，不影响测试通过）。
- `cd frontend && pnpm exec vue-tsc --noEmit --skipLibCheck`
  - 结果：失败。
  - 备注：仓库当前存在大量与本次需求无关的历史类型错误，未在本次需求中清理。
- `cd frontend && pnpm exec vue-tsc --noEmit --skipLibCheck 2>&1 | rg "src/views/management/permission/index.vue|src/service/api/org-type-permissions.ts"`
  - 结果：无输出，说明本次涉及的后台权限页文件未新增类型错误。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过。
- 协议样例解析：
  - 对 `历史记录读取协议.md` 中的 `0x4C / 0x4D` 示例载荷执行解析校验。
  - 结果：
    - `0x4C` 成功解析出 `protocolVersion=1`、`currentRecordAddress=76`、`currentRecordCount=61`
    - `0x4D` 成功解析出 `2024-10-11 12:12:17`、`totalVoltageV=47.94`、`lowestVoltageMv=2988`、`highestVoltageMv=3008`、`socPct=8`、`sohPct=100`、`mosTempC=26`
  - 备注：文档示例整帧 CRC 与当前协议库校验口径不一致，因此本次采用“示例载荷切片”进行字段级验证；不影响实际运行时对真实设备返回帧的解析路径。

## 3. 待补充手工验收
- [ ] 后台“系统管理 > 权限管理”出现“移动端权限”页签，且仅展示“历史记录”权限项
- [ ] `PACK_FACTORY / DEALER / STORE / APP_USER` 四类用户分别保存“历史记录”权限后，刷新页面回显正确
- [ ] `GET /api/v1/org_type_permissions/mobile_ui_codes/me` 对终端用户仅命中 `APP_USER`，对机构用户仅命中自身 `org_type`
- [ ] 未分配权限时，设备详情页隐藏“历史记录” Tab，且不会挂载历史记录组件
- [ ] 已分配权限时，设备详情页显示“历史记录” Tab，蓝牙 / MQTT / 仪表临时连接三种入口显隐一致
- [ ] 设备详情底部 4 个一级 Tab 切换正常
- [ ] 历史记录二级切换激活态正确，文案为“总计 / 明细”
- [ ] 切入参数设置 / 历史记录时轮询暂停，离开后恢复
- [ ] 状态记录默认展示最近时间的 1 条，组件内部滚动或点击页脚可继续加载更早 1 条
- [ ] 当首屏仅 1 条不足以形成滚动时，会自动补载到至少 2 条，并保持“最近时间优先”
- [ ] `日志1=4` 时卡片右上角显示“上电启动 / Power-On Startup”
- [ ] `日志1` 的新增枚举值（如 `5 / 22 / 35 / 101 / 117`）按完整版协议显示正确中英文文案
- [ ] 状态记录卡片显示剩余容量，且温度状态、充放电状态位标签按协议位定义正常展示
- [ ] 地址 `26` 的 `BIT4/BIT5` 不再在前端展示，`BIT6/BIT7` 仍正常显示“正在放电 / 正在充电”
- [ ] 地址 `23` 的电压状态标签与源 PDF 截图一致，尤其是“总压过放恢复 / 电芯过放恢复 / 电压过压保护”
- [ ] 蓝牙、MQTT/Socket Bridge、仪表临时连接三种会话均完成一轮读取验证
- [ ] 无记录 / 不支持 / 读取失败状态展示符合预期
- [ ] 观察控制台日志，确认可看到 `0x4C / 0x4D` 的发送帧、返回帧、解析结果，以及批量失败时的单条回退日志
