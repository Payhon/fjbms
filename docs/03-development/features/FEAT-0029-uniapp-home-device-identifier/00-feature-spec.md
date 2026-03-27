# FEAT-0029 UniApp 首页设备标识展示切换 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-03-27
- related_feature: FEAT-0029
- version: v0.1.0

## 1. 背景与目标
当前 `fjbms-uniapp` 首页“我的设备”卡片在设备名称下方显示的是 `device_number/UUID` 口径，无法体现设备真实接入标识。业务要求改为按通讯类型展示：
- 蓝牙设备显示 MAC
- 4G 设备显示 ICCID
- 蓝牙+4G 双模设备优先显示 ICCID

## 2. 范围（In Scope / Out of Scope）
In Scope:
- 后端首页设备列表接口补充 `iccid` 字段。
- UniApp 首页卡片副标题按 `bms_comm_type` 显示 `MAC/ICCID`。
- 标识缺失时回退到当前旧值，避免卡片空白。
- 同步功能文档与项目看板。

Out of Scope:
- 不改设备详情页、筛选项、扫码页或其他列表页展示。
- 不改搜索接口与搜索字段定义。
- 不新增掩码、复制按钮或新的设备标识交互。

## 3. 用户价值
- 首页设备列表展示更符合设备通讯形态，便于用户快速识别设备。
- 双模设备优先显示 ICCID，便于 4G 设备现场核对。
- 缺失字段时保持兼容，不影响现有设备浏览。

## 4. 验收标准
- `bms_comm_type=1` 的设备在首页副标题显示 MAC。
- `bms_comm_type=2` 的设备在首页副标题显示 ICCID。
- `bms_comm_type=3` 的设备在首页副标题显示 ICCID。
- 若目标字段为空，则回退显示旧副标题，不出现空行。

## 5. 风险与约束
- 线上设备存在历史数据，部分设备只有 `comm_chip_id` 没有 `iccid`，后端需兼容映射。
- 首页卡片展示逻辑应集中在首页数据映射层，避免组件层重复判断通讯类型。
- 需保持蓝牙自动连接、长按菜单等首页现有能力不受影响。

## 6. 回滚方案
- 回滚后端首页列表 `iccid` 字段扩展。
- 回滚 UniApp 首页副标题映射逻辑，恢复显示 `device_number`。
