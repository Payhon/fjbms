# 富嘉 BMS 查询协议开发指南（易读版）

本指南用于前端（uni-app）/后端在实现 **BLE/串口** 通讯时快速落地，避免“寄存器地址不固定”导致的误读。

原始协议文档请参考：`doc/oriigin/device_comm_protocol_basic.md`。

---

## 1. 从机回复如何判定“完整包”

从机回复格式（原文第 52 行起）包含：

- **头码**：`0x7F, 0x55`
- **字节数量 N**：位于偏移 `5`（仅对读回复有效）
- **CRC**：`CRCL, CRCH`
- **尾码**：`0xFD`

实现建议：

- BLE notify 可能分包（chunk），**不能假设一次 notify 就是完整帧**。
- 读回复（功能码 `0x03` / `0xFF`）可用 `byteCount` 推导长度：
  - `expectedLen = 9 + byteCount`
  - 当缓冲区长度 `>= expectedLen` 且尾码为 `0xFD` 时，才进行 CRC 校验与解析。

本项目中对应实现：`fjbms-uniapp/common/lib/bms-protocol/uni-ble-transport.ts` 的 `FrameCollector.tryShiftOneValidFrame()`。

---

## 2. 动态寄存器地址（最重要）

协议的状态寄存器分两段：

- **固定区**：`0x100 ~ 0x140`
- **变长区**：从 `0x141` 开始顺延（文档中用 `...` 表示）

变长区的地址与 **电池串数 S**、**电芯温度数量 N** 相关，因此必须先读寄存器 `0x100`：

- `S = 高字节(H)`
- `N = 低字节(L)`

### 2.1 变长区字段顺序（从 0x141 开始）

按寄存器（16-bit）为单位，顺序为：

1. 电芯电压数组 `[S]`
2. 电芯温度数组 `[N]`
3. 硬件型号（32 bytes = 16 regs）
4. 电池组编号（32 bytes = 16 regs）
5. BMS 板编码（32 bytes = 16 regs）
6. 蓝牙 MAC 地址（10 bytes = 5 regs，通常前 6 bytes 有效）

### 2.2 推荐的地址计算公式

以寄存器为单位：

- `CELL_VOLTAGES_START = 0x141`
- `CELL_TEMPS_START = CELL_VOLTAGES_START + S`
- `HW_MODEL_START = CELL_TEMPS_START + N`
- `BATTERY_GROUP_ID_START = HW_MODEL_START + 16`
- `BOARD_CODE_START = BATTERY_GROUP_ID_START + 16`
- `BLUETOOTH_MAC_START = BOARD_CODE_START + 16`

---

## 3. 一次性读取“硬件型号/电池组编号/板编码/蓝牙MAC”

这 4 个字段是连续的，因此在已知 `S/N` 后可以 **一次读完再分段解析**：

- 起始地址：`HW_MODEL_START`
- 寄存器数量：`16 + 16 + 16 + 5 = 53 regs`

在 uni-app 中对应封装：

- 读取 S/N：`BmsClient.readSn()`
- 读取并解析四个字段：`BmsClient.readIdentityInfo()`

文件位置：`fjbms-uniapp/common/lib/bms-protocol/client.ts`

---

## 4. “BMS板UUID(0xFF)” 与 “BMS板编码(状态区)” 的区别

协议中存在两个容易混淆的“唯一标识”：

1. **BMS 板 UUID（功能码 `0xFF`）**：属于读指令功能，返回 16 bytes。
2. **BMS 板编码（状态区字段）**：位于变长区（长度 32 字符），地址需要按 `S/N` 动态计算（`BOARD_CODE_START`）。

业务需要哪个字段以产品定义为准。

---

## 5. 任意寄存器范围读取 + 语义化解析（PARAM_DEFS）

为了便于后续开发，本项目提供“按地址读一段寄存器，并对照 `param-registry.ts` 语义化解析”的方法：

- `BmsClient.readParamsByAddressRange(startAddress, quantity)`

解析规则：

- 仅解析 `PARAM_DEF_BY_KEY` 中 **valueType 为 `u8/u16/u32/str`** 的参数（`statusPath` 不在本方法内解析）。
- 仅解析“**完全落在请求范围内**”的参数：
  - `u32` 需要 2 个寄存器都在范围内
  - `str` 需要整段字符串占用的寄存器都在范围内
- 返回对象 key 使用 `param-registry.ts` 定义的变量名转换：`SCREAMING_SNAKE_CASE -> camelCase`

相关实现：

- `fjbms-uniapp/common/lib/bms-protocol/client.ts`：
  - `readParamsByAddressRange()`
  - `decodeParamsByAddressRange()`
- `fjbms-uniapp/common/lib/bms-protocol/param-registry.ts`：`PARAM_DEF_BY_KEY`

---

## 6. 示例（uni-app）

```ts
import { BmsClient, createUniBleBmsTransport } from '@/common/lib/bms-protocol'

const transport = createUniBleBmsTransport({ requestTimeoutMs: 8000, logger: console })
const client = new BmsClient({ transport, logger: console })

await transport.connect({ deviceId })

// 1) 读取“动态身份信息”
const identity = await client.readIdentityInfo()
console.log(identity)

// 2) 读取并语义化解析一段配置寄存器（示例：0x400 开始读取 20 个寄存器）
const params = await client.readParamsByAddressRange(0x400, 20)
console.log(params)
```

