# FEAT-0029 UniApp 首页设备标识展示切换 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-03-27
- related_feature: FEAT-0029
- version: v0.1.0

## 1. 测试范围
- 后端首页设备列表 `iccid` 返回。
- UniApp 首页设备副标题按通讯类型切换显示。

## 2. 测试环境
- 本地开发环境
- 日期：2026-03-27

## 3. 用例结果
- `backend`
  - 命令：`cd backend && go test ./internal/model ./internal/service`
  - 结果：通过
  - 备注：出现 `github.com/shirou/gopsutil/disk` 的 macOS 弃用告警，不影响本次功能
- `fjbms-uniapp`
  - 命令：`cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过
  - 静态自检：已完成首页卡片展示与类型映射检查
  - 真机/小程序联调：待执行

## 4. 缺陷与风险
- 若历史设备 `iccid` 与 `comm_chip_id` 均为空，将继续回退旧副标题。
- 需用真实蓝牙/4G/双模设备各验证一条首页展示链路。

## 5. 结论
- 定向校验已通过，代码可进入真机/小程序联调验收。
- 下一步重点验证蓝牙、4G、双模设备在首页的副标题显示是否符合预期。
