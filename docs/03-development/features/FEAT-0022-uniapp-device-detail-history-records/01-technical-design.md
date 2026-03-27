# FEAT-0022 UniApp 设备详情页历史记录功能 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-03-22
- related_feature: FEAT-0022
- version: v0.1.0

## 1. 协议层设计
- 在 `common/lib/bms-protocol/frame.ts` 中扩展功能码：
  - `0x4C`：`HISTORY_PROTECTION_COUNT`
  - `0x4D`：`HISTORY_STATUS_RECORD`
- 在 `parseFrame()` 中将 `0x4C / 0x4D` 纳入读帧判断逻辑，复用现有头尾、CRC、错误帧分支。
- 新增 `history-parser.ts` 负责载荷级解析：
  - `parseHistoryProtectionPayload(data)`
  - `parseHistoryStatusPayload(data, startIndex)`
- `0x4C` 解析为结构化计数对象；对样例中预留区缺失场景做容错，只要求最小有效字段长度满足即可。
- `0x4D` 解析为记录数组：
  - 时间字段按 BCD 转换为 `yyyy-MM-dd HH:mm:ss`
  - 电流按有符号 16 位、`10mA` 单位转 `A`
  - 温度按 `raw - 40`
  - 状态位拆成四组布尔字典，供 UI 聚合标签使用
  - 依据 `历史记录读取协议(完整版).md`，地址 `26` 的 `BIT4/BIT5` 标记为“暂时不用解析”，前端只展示 `BIT6/BIT7`

## 2. Client 接口
- 在 `BmsClient` 中新增：
  - `readHistoryProtectionCounters()`
  - `readHistoryStatusRecords(startIndex, quantity)`
- 若设备返回错误帧或单字节 `0xFF`，上述接口返回 `null`，由 UI 统一映射为“不支持历史记录”。
- `readHistoryStatusRecords()` 单次限制 `1~6` 条，保持与协议文档一致。

## 3. 页面与交互
- `pages/device-battery/detail.vue`
  - `activeTab` 从 `0 | 1 | 2` 扩展到 `0 | 1 | 2 | 3`
  - 新增底部一级菜单“历史记录”
  - 在 `onReachBottom` 中转发给 `history-tab.vue` 的 `loadMoreStatusRecords()`
  - 将“参数设置 / 历史记录”统一纳入暂停轮询范围
- `pages/device-battery/components/history-tab.vue`
  - 二级切换默认停留在“保护次数记录”
  - 首次进入当前分段时再发请求，避免无谓访问
  - “状态记录”先依赖 `0x4C` 的 `currentRecordCount` 得到总条数，再按尾部向前分页读取 `0x4D`
  - 页底加载更多采用页面滚动触底触发，不单独引入内部固定高度滚动容器

## 4. UI 结构
- 保护次数记录：
  - 顶部 2x2 摘要卡：总记录数、当前地址、累计充电时长、累计放电时长
  - 下方按“温度类 / 压流类 / 充放电类 / 系统类”分组，每行 `名称 + 次数`
- 状态记录：
  - 头部：时间主标题 + 记录序号 + 日志码徽标
  - 中部：2 列紧凑指标卡
  - 底部：状态标签区与附加明细网格
- 状态展示优先级：
  - 无连接
  - 加载中
  - 不支持
  - 读取失败
  - 空数据
  - 正常内容

## 5. 多语言与映射
- 在 `lang/zh-CN.ts`、`lang/en-US.ts` 的 `deviceDetail` 节点下新增：
  - `tabs.history`
  - `history.*`
- 历史日志码按协议文档中的枚举值配置中英文映射。
- `日志1` 映射以 `doc/oriigin/历史记录读取协议(完整版).md` 为准，补齐 `5~17`、`22~48`、`101~120` 等之前缺失的枚举值。
- 状态位标签分组管理，UI 层通过 `deviceDetail.history.statusFlagLabel.<group>.<key>` 动态取文案。
