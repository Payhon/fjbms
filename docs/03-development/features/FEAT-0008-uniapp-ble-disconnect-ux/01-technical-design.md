# FEAT-0008 UniApp 蓝牙信号展示与手动断开连接优化 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-04
- related_feature: FEAT-0008
- version: v0.1.0

## 1. 方案概览
- 扫描页：根据 RSSI 阈值映射为 0~4 档信号强度，UI 仅展示信号柱图。
- 连接管理：在 BLE 缓存层新增“立即断开”能力，绕过空闲超时等待。
- 交互入口：
  - 设备详情页：连接状态区域新增断开按钮（仅蓝牙已连接时可见）。
  - 首页设备卡片：连接状态下方新增断开图标按钮（仅蓝牙连接设备可见）。

## 2. 接口与数据结构
- 新增缓存层 API：`disconnectBleClient(mac): Promise<boolean>`
  - 等待 inFlight 连接任务完成。
  - 清理定时器与缓存并调用 transport 断连。
- 设备详情组合式新增：`disconnectBluetooth()`
  - 仅 `connType===bluetooth` 时生效。
  - 调用 `disconnectAll()` 后执行 `disconnectBleClient`。

## 3. 关键流程
1. 首页断开流程：
   - 仅当卡片 `connectType===bluetooth` 才响应。
   - 校验缓存存在 -> 调用 `disconnectBleClient` -> 更新卡片为 mqtt/offline。
2. 详情页断开流程：
   - `showBleDisconnectBtn = connType===bluetooth && !connecting`。
   - 用户点击后调用 `disconnectBluetooth()`，并提示成功/失败。
3. 扫描信号流程：
   - 根据 RSSI 阈值（-60/-70/-80/-90）映射强度等级。
   - UI 显示 4 柱形图激活态。

## 4. 安全与权限
- 本次变更仅前端连接控制，不新增后端接口权限面。
- 断开操作限定在当前设备的 BLE MAC，不跨设备操作。

## 5. 测试策略
- 静态检查：TypeScript 编译。
- 交互验证：
  - 扫描页信号图标渲染。
  - 首页与详情页断开按钮显隐和点击行为。
  - 非蓝牙态不触发断开逻辑。

## 6. 兼容性与迁移
- 保持现有 BLE/MQTT 自动连接策略不变。
- 不涉及数据库、协议字段、接口兼容性改动。
