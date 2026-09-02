# FEAT-0073 设备详情 UUID 复制与 4G IMEI 展示 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-08-30
- related_feature: FEAT-0073
- version: v0.1.0

## 1. 方案概览

- 后端 APP 电池详情查询直接读取 `device_batteries.imei` 并返回可空 `imei`。
- UniApp 详情页在仪表盘 Tab 顶部增加 UUID 信息卡；复制只使用当前 `item_uuid`，不使用平台 `device_id/device_number`。
- 仪表盘标识选择抽取为纯函数，统一决定 IMEI/MAC 类型和值；通用仪表组件不再使用 MAC 专属属性名。

## 2. 接口与数据结构

- `GET /api/v1/app/battery/detail/{device_id}` 响应新增：
  - `imei: string | null`
- UniApp `AppBatteryDetail` 同步新增：
  - `imei?: string | null`
- 仪表盘标识解析结果：
  - `kind: 'imei' | 'mac'`
  - `text: string`，4G 为 `IMEI: <值或 ->`，蓝牙为格式化 MAC 或 `-`。

## 3. 关键流程

1. 页面加载详情接口并获得 `item_uuid`、`bms_comm_type`、`ble_mac`、`imei`。
2. 仪表盘 Tab 在数据加载态和正常内容之前渲染 UUID 卡片；缺失值显示横杠并禁用复制。
3. 有效 UUID 点击后调用 `uni.setClipboardData`，成功/失败分别显示本地化 Toast。
4. 标识策略按 `bms_comm_type` 和当前 `connType` 选择：
   - `2/3` 且 `connType !== 'bluetooth'`：严格显示 IMEI，缺失显示横杠。
   - 其他场景：显示 `battery.ble_mac -> status.identity.bluetoothMac -> '-'`，有效 MAC 使用冒号格式。
5. App/H5 通过仪表插槽渲染标识，微信小程序 Canvas 使用同一文本属性绘制，并在属性变化时重绘。

## 4. 安全与权限

- 复用现有 APP 电池详情权限校验，不增加接口或权限点。
- IMEI 仅随用户已有权访问的设备详情返回。
- 复制行为只在本机剪贴板发生，不上传、不记录日志。

## 5. 测试策略

- 后端 SQLite 服务测试验证详情响应透出 IMEI。
- 标识策略测试覆盖纯 4G、双模 MQTT、双模蓝牙、纯蓝牙、IMEI 缺失、MAC 格式化和 UUID 空值。
- 执行 Go 定向测试、UniApp TypeScript、Vue SFC 编译、Swagger 生成和差异检查。
- 375px 窄屏及微信小程序、Android/iOS 运行时验证完整 UUID、复制和仪表标识布局。

## 6. 兼容性与迁移

- 新增响应字段向后兼容旧客户端，无数据库迁移。
- 历史设备 IMEI 为空时明确显示 `IMEI: -`，不把其他编号伪装成 IMEI。
- 保留当前导航标题、页面连接状态和所有实时数据路径。
