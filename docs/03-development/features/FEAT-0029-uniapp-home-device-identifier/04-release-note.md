# FEAT-0029 UniApp 首页设备标识展示切换 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-06-12
- related_feature: FEAT-0029
- version: v0.1.0

## 1. 发布内容
- 首页“我的设备”卡片副标题改为按通讯类型显示 MAC / IMEI。
- 4G/双模 BMS 设备优先显示 IMEI；IMEI 缺失时继续回退 ICCID/历史 `comm_chip_id` 兼容值。
- 后端首页设备列表接口新增 `imei` 字段，并保留 `iccid` 字段。

## 2. 影响范围
- `backend/` APP 首页设备列表接口
- `fjbms-uniapp/` 首页设备卡片展示

## 3. 升级步骤
1. 部署后端代码。
2. 发布 UniApp 新版本。
3. 用蓝牙、4G、双模设备分别验证首页卡片副标题，其中 4G/双模 BMS 应显示 IMEI。

## 4. 回滚步骤
1. 回滚 FEAT-0029 相关前后端代码。
2. 首页卡片恢复显示旧的 `device_number/UUID` 副标题或上一版 MAC/ICCID 口径。

## 5. 已知问题
- 当前只调整首页卡片展示口径，不改设备详情和筛选字段。
