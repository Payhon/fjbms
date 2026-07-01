# FEAT-0061 设备详情充放电控制工厂命令 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-06-25
- related_feature: FEAT-0061
- version: v0.1.0

## 1. 实施记录
1. 后端设备参数权限树新增 `禁止充电`、`禁止放电`、`允许充放电` 三个出厂配置权限节点。
2. 后端权限归一化单测新增三个 `factory:*` key 的大小写 canonical 断言。
3. Web BMS 设备详情高级设置工厂命令列表新增三项 action，并补齐中英文文案。
4. UniApp 设备详情高级参数出厂配置列表新增三项 action，并补齐中英文文案。
5. 不新增 SQL 迁移，既有受限组织需管理员手动勾选新权限。

## 2. 当前状态
- 代码改造已完成。
- 后端权限树单测、Web 受影响文件 ESLint、UniApp TypeScript 校验、空白检查和协议帧校验均已通过。
- Web 显式全量 `vue-tsc` 仍受仓库既有类型错误阻塞；过滤输出未发现本次修改的 BMS 面板和 `bms.json` 词包报错。
- 真实设备通讯和受限账号运行态回归待目标环境验证。
