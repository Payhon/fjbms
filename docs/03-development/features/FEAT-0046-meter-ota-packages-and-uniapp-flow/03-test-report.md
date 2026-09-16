# FEAT-0046 仪表 OTA 升级包与 UniApp 独立升级链路 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-09-12
- related_feature: FEAT-0046
- version: v0.1.9

## 2026-09-12 动态ACK超时本地验证

- 结果：累计27项本地脚本通过（原26项回归加新增可控时钟测试），不是硬件验收。覆盖Boot时序/运行参数/动态超时、实际BLE/MQTT transport、BLE能力与取消、MQTT响应匹配/唤醒/fjia2、缓存释放、OTA页面会话、仪表恢复、日志、OTA目标策略、轮询以及扫描/参数/4G兼容路径。
- 可控时钟：0x50～0x53无ACK在0/800/1250/1700ms发送、2150ms耗尽；0x54在0/5000/5450/5900ms发送、6350ms耗尽。首发799ms、完成4999ms和重发449ms收到ACK即结束等待，无残留定时器。用户补充的完成重发450ms已覆盖，非每次5秒。
- 验证同包重试、三次共享恢复预算、status=3重复ACK、status=1重新准备及其800/450重试、所有非ACK错误立即失败、0x50与4G进入Boot的耗尽兼容。模拟1151 ACK后300ms页保护，1152丢ACK仍重发1152，不叠加页等待；64/128/256/512/1024字节页边界回归通过。
- 页面真实SFC处理函数验证BLE/MQTT五种命令的首次与重发timeoutMs均透传，旧450ms上限不再截断800ms；零宽限不调度Android读探测，非零宽限的底层兼容测试仍保留。
- TypeScript检查与params-tab.vue/detail.vue的SFC脚本和模板编译通过；根仓库和UniApp的git diff --check通过。未修改普通连接超时或BLE会话恢复逻辑。
- Android/iOS微信小程序不退出进程连续20次、App三链路、4G连续20次和实际版本/弱信号验证仍待完成，保持in_progress。未提交、推送或部署。

新增时序测试无需安装依赖，在fjbms-uniapp目录执行：

```sh
node -e 'const fs=require("fs"),ts=require("typescript");require.extensions[".ts"]=(m,f)=>m._compile(ts.transpileModule(fs.readFileSync(f,"utf8"),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText,f);require("./common/lib/bms-protocol/boot-ota-dynamic-timeout.test.ts")'
pnpm exec tsc --noEmit --pretty false
git diff --check
```


## 2026-09-10 会话清理与自动恢复验证

- 本地通过26项脚本：16项OTA/transport/会话定向回归（Boot时序、运行参数、Boot transport、BLE OTA、BLE连接取消、MQTT响应匹配/唤醒/fjia2、缓存释放、OTA页面会话、仪表会话恢复、OTA日志、透传OTA策略、轮询策略、扫描进入/退出策略两项），以及10项兼容回归（扫描协调、扫描错误、扫码路由、面板交接、数据仲裁、仪表扫描交接、仪表透传等待、参数刷新、4G在线策略、设备标识）。
- 新增断言：原生断连缓存失效；重复关闭只派发一次；回调缺失/失败不放行同设备；迟到成功解除屏障；另一设备和扫描租约可用；旧监听/收尾不删除新缓存；租约等待期间新增引用不得被旧释放关闭；取消连接后迟到create必须先收尾再close；旧排队请求不能继续派发。
- 新增恢复断言：三种升级目标、原升级成功/失败、原生断连/仪表保持连接、实际版本、仪表不读BMS；1秒等待、最多两次、超时/退出、迟到操作不能重新连接/写UI；Boot清理完成才恢复；Boot前失败及MQTT不恢复；恢复不改变原OTA结果，调试关闭无恢复日志回调。
- 超时覆盖关闭、连接、状态读取三个阶段；恢复中切换设备后旧任务不能覆盖新client。BLE OTA/恢复期间禁止切换Tab销毁组件，普通Tab及MQTT的既有交互不变。
- 执行方式：使用项目已安装的TypeScript `transpileModule` 注册Node临时 `.ts` require与 `@/` 解析hook，在独立Node进程运行上述 `*.test.ts/js`；未下载或新增测试依赖。仪表会话可直接运行 `node pages/device-battery/instrument-session-recovery.test.js`。
- `pnpm exec tsc --noEmit --pretty false`、`detail.vue`/`params-tab.vue` 的Vue SFC脚本及模板编译、根仓库与UniApp `git diff --check` 通过。
- 待真机：Android/iOS微信小程序关闭调试且不退出小程序，扫描仪表透传BMS各连续20次；成功退出重进、失败后重连、弱信号、交替版本读回。另补App、直连BMS、仪表自身、MQTT/4G及参数读写/后台转发回归；保持 `in_progress`。

## 1. 自动化验证
- [x] `cd backend && go test ./internal/service/...`
- [ ] `cd frontend && pnpm build`
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`

## 2. 手工验证清单
- [ ] 后台升级包管理页双 TAB 可切换。
- [ ] BMS TAB 新增/编辑/删除维持原有行为。
- [ ] 仪表 TAB 仅要求名称、固件文件、说明。
- [ ] OTA 任务页和电池列表批量 OTA 只出现 BMS 升级包。
- [ ] 蓝牙仪表详情页隐藏旧 OTA 检测入口与红点。
- [ ] 蓝牙仪表详情页可拉取仪表固件列表、选择固件、确认升级。
- [ ] 仪表升级时 Boot 目标地址固定为 `0xFC`。
- [ ] 蓝牙仪表会话显示独立 BMS 升级卡片，未检测到BMS状态时按钮禁用。
- [ ] UUID成功、UUID失败后型号降级、身份缺失阻断三条检查分支符合预期。
- [ ] 仪表透传 BMS 首帧为 `55 FE 01 50 00 00 0C 39 FD`，且使用标准BMS时序。
- [ ] 仪表自身 `0xFC`、透传BMS `0x01`、直接BMS `0x01` 三条链路互不影响。
- [ ] 透传BMS首/中/末包ACK在670ms内缺失时只重发同一包，设备 `requested` 可确认前进或请求回退，主机不得跳包。
- [x] 模拟Boot transport验证有效 `0x52` ACK后立即首发；数据阶段结束至 `0x54` 仍约300ms且不超过700ms。
- [ ] 最新时序策略断言 `0x50`～`0x53` 应答450ms、宽限220ms、总670ms后同包重发；每确认4KB后等待300ms再发下一页首包，页首包重试不重复等待。BLE `0x54` 最多8次、间隔800ms、单窗口6400ms，MQTT/4G保持单次发送和5000ms窗口。
- [x] MTU策略测试覆盖512、临界78、低于78、API失败与成功回调无MTU字段；Boot transport测试覆盖75字节最小 `0x53` 完整帧禁止分片、缺失 `write` 属性不误判带响应写。
- [x] 模拟延迟ACK验证传输进度在 `0x53` 应答前不增加、收到有效应答后才增加。
- [ ] Android 微信小程序与 Android App 的直连BMS、仪表自身、仪表透传BMS三条链路分别连续成功20次，每条至少一次弱信号场景，并确认升级后版本变化。
- [ ] iOS BLE与MQTT/4G各完成一次450ms应答窗口冒烟回归。

## 3. 待补充
- 2026-04-21：已复测 `cd backend && go test ./internal/service/...`，通过。
- 2026-04-21：已复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：修复 Android 仪表扫描进入详情连接候选、iOS 0x53 超时重试、`status=5` 文案后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：继续修复 Android 仪表详情“连接中”无退出问题，增加 BLE 连接队列与 `createBLEConnection` 超时出口后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：继续修复 Android 仪表 OTA 17% 写包超时，调整仪表 `0x53` 超时和 Android 写入节奏后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：继续修复 Android 仪表 OTA 13% 写包超时，针对 4KB 固件边界增加 Android 仪表 OTA 专用边界等待参数后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：根据 Android 仪表 OTA 10% 卡住日志确认 20 字节 BLE 分片会导致首个 `0x53` 无 ACK，已撤回分片并保持 Boot 帧单次 BLE 写入，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：根据 Android 仪表 OTA 95% finalize 日志确认数据包已完整 ACK，优化 `0x54` 超时/断开成功收敛与静默预期超时日志后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：优化蓝牙扫描页停止扫描与扫描超时状态复位后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：根据 iOS 仪表 OTA 95% finalize 日志确认全部数据包已 ACK，补齐 iOS `0x54` 后 `no device` 断连成功收敛与静默 finalize 重试策略后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：根据 iOS 成功升级日志确认 `0x53` 全部 ACK 与 `0x54` finalize 收敛，并优化 iOS 扫描进详情直连候选与取消旧连接后的锁等待，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-27：新增开发者模式下仪表 OTA 端上调试日志、复制与清空能力后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-27：优化微信小程序主包体积，将 OTA 调试日志模块迁入设备详情分包并删除未引用 `static/js/moment.js` 后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-28：根据微信小程序仪表 OTA 95% 日志，补齐最后一个 `0x53` 写入遇到 `10006/writeValueToCharacteristics` 时进入 `0x54` finalize 的成功收敛策略，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-28：统一蓝牙 BMS 与蓝牙仪表在 Android/iOS 运行时的 OTA 末尾边界策略，仪表 Android 专用写包节奏保持独立，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-28：根据小程序仪表 OTA 成功界面但版本未变化日志，将仪表 OTA 改为 `0x53` 全部 ACK + 延迟 2s + `0x54 status=0` 的严格成功条件，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-28：借鉴旧版微信小程序 OTA 可用实现，蓝牙 BMS 与蓝牙仪表 OTA 均增加 `0x54` 300ms/600ms/900ms 补发；两者均要求 `0x54 status=0` 才判定成功，仪表额外兼容 `0xFD` Boot 回包源地址，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-28：优化 Android 仪表 `0x53` ACK 驱动发包速度，取消默认 ACK 后固定等待、降低最小帧间隔与 4KB 边界等待，并增加超时后的自动慢速保护，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-07-21：增加 BLE OTA 独占通讯会话并将蓝牙 BMS/仪表 `0x54` 收敛为单个 5s 严格应答窗口；静态检查 `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false` 通过，待 Android、iOS 与微信小程序真机验证 OTA 启动等待和 `0x54 status=0` 收敛。
- 2026-08-03：后端透传身份解析与升级包匹配定向测试通过；UniApp `pnpm exec tsc --noEmit --pretty false` 通过。策略脚本覆盖卡片门控、UUID规范化/降级请求和 `0x01` Boot查询帧，真机验收仍待执行。
- 2026-08-05：新增 OTA 时序常量与模拟 Boot transport 测试，临时编译后两项定向测试通过；`pnpm exec tsc --noEmit --pretty false` 与 UniApp `git diff --check` 通过。Android、iOS、微信小程序和4G/MQTT真实设备的700ms时序仍待验收。
- 2026-08-06：BLE `0x54` 时序常量断言与模拟 transport 场景通过：无应答时首发加7次补发共8次且不启动第二轮，`status=0` 提前应答会清理剩余定时器，非零状态会立即失败并清理定时器；MQTT/4G仍为单次发送和5000ms窗口。`pnpm dlx tsx common/lib/bms-protocol/boot-ota-runtime-options.test.ts`、`pnpm dlx tsx common/lib/bms-protocol/boot-ota-timing.test.ts`、`pnpm exec tsc --noEmit --pretty false`、UniApp及文档 `git diff --check` 均通过。真机BLE发送时间戳仍待验收。
- 2026-08-28：BLE与MQTT/4G共享非完成帧应答超时调整为900ms；`pnpm dlx tsx common/lib/bms-protocol/boot-ota-runtime-options.test.ts`、`pnpm dlx tsx common/lib/bms-protocol/boot-ota-timing.test.ts`、`pnpm exec tsc --noEmit --pretty false` 均通过。Android、iOS、微信小程序及4G/MQTT真实设备成功率仍待客户验证。
- 2026-09-02：BLE与MQTT/4G共享非完成帧应答超时由900ms调整为600ms；定向时序断言和类型检查通过，Android、鸿蒙、iOS、微信小程序及4G/MQTT真机成功率继续待客户验证。
- 2026-09-02：共享非完成帧应答超时恢复为450ms，新增MTU选择、API失败/无返回、整帧写入和ACK后进度测试；`pnpm exec tsc --noEmit --pretty false`、临时编译后的运行参数/时序/传输层定向测试及差异检查通过。Android六组连续20次、弱信号、升级后版本变化及iOS/MQTT冒烟仍待真机验收。
- 待执行前端构建复测。
- 待真机联调仪表 OTA 下载与写包流程。
- 待 Android、iOS、微信小程序分别验证仪表透传 BMS OTA 全流程以及升级后版本变化。

## 4. 2026-09-03 本轮本地验证

本节保留本日前一轮“同包重发”方案的本地验证历史，不代表真机验收；第5节是随后执行但已撤销的超时推进试验，现行策略与最新门槛见第6节。

- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`。
- [x] 使用已安装的 `@vue/compiler-sfc` 编译 `detail.vue` 与 `components/params-tab.vue` 的 script/template。
- [x] `pnpm dlx tsx common/lib/bms-protocol/boot-ota-transport.test.ts`：真实BLE/MQTT传输代码接入模拟API，449/500/669ms ACK均一次发送成功；无ACK按670ms配置重发，本轮两条链路均观测约672ms（JS调度误差），不额外叠加220ms。覆盖混合普通/CRC坏帧、分段ACK、旧/未来/错地址ACK、缺失原生写回调、独占取消与队列恢复、普通读探测不泄漏、`0x54` 不误收 `0x53` 或空应答。
- [x] `pnpm dlx tsx common/lib/bms-protocol/boot-ota-timing.test.ts`：ACK前不增长进度，成功旧序号不回退，显式回退有次数上限；设备指定包长不可缩小，非法包长/ACK失败；4KB边界等待、准备/完成300ms，以及严格 `0x54` 成功、拒绝、超时和补发取消均通过。
- [x] `pnpm dlx tsx common/lib/bms-protocol/boot-ota-runtime-options.test.ts`：BLE与MQTT `0x50`～`0x53` 保持450ms、`450 + 220 = 670ms`；既有完成帧策略不变。
- [x] `pnpm dlx tsx common/lib/bms-protocol/uni-ble-transport-ota.test.ts`：MTU512、78、77、协商失败和无具体返回；整帧不分片、Android缺失/双写属性及仅带响应属性、iOS写模式兼容、迟到写失败不影响下一请求。
- [x] `pnpm dlx tsx pages/device-battery/ota-session.test.js`：执行实际页面处理函数及Vue批量watch，验证MTU兼容回退、已知小于78时无Boot写入、设备指定包长超容量时无 `0x53`、BLE/MQTT独占、屏幕与轮询在成功/失败后恢复；100%只在真实 `0x54 status=0` 后显示。
- [x] 普通连接/通讯回归：分别执行 `pnpm dlx tsx` 加 `common/lib/bms-protocol/uni-ble-transport-connect-cancel.test.ts`、`common/lib/bms-protocol/uni-mqtt-socket-transport-response-match.test.ts`、`common/lib/bms-protocol/uni-mqtt-socket-transport.wakeup.test.ts`、`common/lib/bms-protocol/uni-mqtt-socket-transport-fjia2-repro.test.ts`，均通过。
- [x] 页面回归：`pnpm dlx tsx pages/device-battery/detail-polling-policy.test.ts`、`pnpm dlx tsx pages/device-battery/meter-bms-ota-policy.test.ts`、`node pages/device-battery/instrument-session-recovery.test.js`，均通过。
- [ ] Android微信小程序及App：直连BMS `0x01`、仪表自身 `0xFC`、仪表透传BMS `0x01`，六组分别连续成功20次，每组至少一次弱信号并确认升级后版本变化。
- [ ] 4G/MQTT：微信小程序及App分别连续成功20次，至少一次弱网；记录 `requested`、ACK RTT、重发次数及版本变化。超过670ms的真实网络延迟仍可能触发重发，不能仅据本地测试承诺成功率。
- [ ] iOS BLE与4G各至少一次完整升级冒烟；本轮未执行真机、HBuilderX打包、后端/管理端构建或部署，状态保持 `in_progress`。

## 5. 2026-09-03 客户超时推进试验

下列13项脚本在 `fjbms-uniapp/` 以 `pnpm dlx tsx <路径>` 实际执行并通过，均为本地模拟/断言，不是连接真机的验收。

- [x] `common/lib/bms-protocol/boot-ota-transport.test.ts`：实际BLE/MQTT传输代码接模拟API，449/500/669ms迟到ACK被接收；首/中/末包无ACK后发送下一包，BLE观测671/673/673ms、MQTT观测671/670/672ms。超时不发确认进度；真实丢数据时发送序列 `0,1,2,1,2,3` 恢复；全部数据ACK丢失仍进入真实CRC32最终校验，`0x54` 缺失/拒绝失败，只有 `status=0` 成功。
- [x] `common/lib/bms-protocol/boot-ota-timing.test.ts`：准备/重准备后立即首发、默认无4KB额外等待；显式硬件等待参数仍有界；`status=3` 下一游标/有界回退、非法序号、写API超时/断连/取消不跳过，ACK前进度不变，严格完成及补发定时器清理通过。
- [x] `common/lib/bms-protocol/boot-ota-runtime-options.test.ts`：450+220=670、数据阶段零额外等待、末包无ACK可最终校验、BLE/MQTT完成策略不变且无超时假成功。
- [x] `common/lib/bms-protocol/uni-ble-transport-ota.test.ts`：原MTU/整帧/写属性/迟到回调回归通过；当前原生写失败即时拒绝。模拟两段各50ms同步TX日志、原生ACK延迟600ms，先原生写再记录日志后可正常接收；RX日志执行前pending已解除。
- [x] `pages/device-battery/ota-debug-log.test.ts`：6100条日志仅保留最近6000条，Boot内无逐条同步存储或响应式列表替换，复制包含最新日志，退出仅保存一次；重复清理、期间清空、存储失败不破坏结束结果。
- [x] `pages/device-battery/ota-session.test.js`：实际页面函数验证BLE/MQTT、Android/iOS和仪表的数据零等待/严格最终确认配置；MTU兼容与容量拒绝；成功/失败路径释放独占、恢复原帧间隔/日志/屏幕并结束日志缓冲；Vue批量watch不恢复OTA内轮询。
- [x] 普通通讯4项：`common/lib/bms-protocol/uni-ble-transport-connect-cancel.test.ts`、`common/lib/bms-protocol/uni-mqtt-socket-transport-response-match.test.ts`、`common/lib/bms-protocol/uni-mqtt-socket-transport.wakeup.test.ts`、`common/lib/bms-protocol/uni-mqtt-socket-transport-fjia2-repro.test.ts`。
- [x] 页面策略3项：`pages/device-battery/detail-polling-policy.test.ts`、`pages/device-battery/meter-bms-ota-policy.test.ts`、`pages/device-battery/instrument-session-recovery.test.js`。
- [x] `pnpm exec tsc --noEmit --pretty false`；已安装Vue SFC编译器对 `detail.vue` 与 `components/params-tab.vue` 的script/template编译通过。
- [ ] Android微信小程序/App的三条BLE链路六组各连续20次、每组至少一次弱信号并确认升级后版本；4G两端各20次及弱网、iOS BLE/4G冒烟仍待真机。新日志应含同包retry/recovery、发送序号、设备requested与最终状态；旧试验字段 `timeoutAdvances` 已随超时跳包撤销，不能再作为验收证据，也不能用发送完毕代替验收。
- [ ] 本轮未运行真机OTA、HBuilderX打包、后端/管理端构建或部署；不将静态/模拟测试称作100%成功，保持 `in_progress`。

## 6. 2026-09-04 页边界失败复盘与最新验收

本节取代第5节的试验策略；第5节仅保留为已执行但已撤销的历史。本轮尚未完成真机验收，未勾选项不能以旧脚本结果替代。

- [x] 失败日志因果链复核：`_resources/ble-upgrade-log-20260904-2-failure.txt` 中包1151确认 `requested=1152`，约5ms后发送位于18×4KB边界的包1152；该包无ACK后客户端连续跳发1153～1162，设备没有更新游标，最终原生BLE写失败。日志显示75字节整帧小于185字节写容量，排除MTU/分片作为此次直接原因。
- [x] 历史证据交叉检查：Android历史日志曾在新页首包64、128失败，启用页等待的样例完成全部数据；20260904-1参考日志在页边界存在至少约93ms的实际间隔，但最终未收到真实 `0x54`，因此只用于证明页边界节奏，不能作为完成确认样例。
- [x] 数据状态机：分别模拟首包、中途包、末包ACK缺失，断言首次重发约在 `450+220=670ms` 且发送序号/载荷完全相同；达到有界次数后失败，任何超时均不增加本地游标、确认水位或进度。
- [x] 设备游标：覆盖 `status=0/status=3` 的前进、重复、回退、非法未来值及反复无进展，断言下一发送包只来自合法 `requested`；回退不重置恢复预算，只有新的确认高水位可重置。
- [x] 4KB边界：覆盖64/128/256/512/1024字节协议档位，断言每确认整页后、下一页首包前等待300ms；同一页首包自身重试不重复等待，设备回退后重新跨越边界会再次保护，最后不足一页不产生额外页等待。
- [x] 数据完整性：末包无ACK不得进入 `0x54`，只有 `requested == packetTotal` 才允许完成阶段；进度只随设备确认更新，不能以发送完毕显示100%。
- [x] 完成阶段：覆盖真实 `0x54 status=0`、非零状态、单纯超时、写入前断连、数据未完整断连、仪表透传BMS断连、MQTT/4G断连，以及“直连BMS或仪表自身BLE全部数据已确认、至少派发过一次 `0x54` 后明确原生断连”的窄化兼容分支；仅最后一种断连场景可按设备重启收敛。
- [x] 日志性能：1585个 `0x53` 数据包保留1585条紧凑结构化 ACK，每条含 `seq/status/requested/RTT`；Boot 层不重复记录 `0x53` 完整十六进制，transport 层完整十六进制只保留首包、末包、4KB边界包、同包重试和异常；会话头未因包数丢失，Boot期间不逐条落盘或触发响应式全量复制，结束后集中发布/保存。
- [x] 已执行Boot时序、运行参数、BLE/MQTT实际transport、页面OTA会话、日志精简、普通MQTT响应/wakeup/fjia2、BLE连接取消、轮询与仪表透传策略回归、TypeScript及详情/参数SFC编译；全部通过。实际命令为 `pnpm dlx tsx` 对应测试文件、`node pages/device-battery/instrument-session-recovery.test.js`、`pnpm exec tsc --noEmit --pretty false`，并执行 `git diff --check`。
- [ ] 真机门槛：Android微信小程序与App的直连BMS、仪表自身、仪表透传BMS六组各连续成功20次，每组至少一次弱信号并核对版本变化；Android微信小程序/App的4G OTA各20次且至少一次弱网；iOS BLE三条链路与4G各完成一次冒烟。每次核对页边界等待、同包重发、最终确认/断连原因及升级后版本，全部完成前保持 `in_progress`。

## 7. 2026-09-04 Android BLE传输层定向回归

- [x] 新失败日志复核：包0～191持续正常，包192在300ms页保护后初发及5次同序重发仍无可解析ACK；MTU 185、ATT容量182、帧长75、RSSI -45，且失败前帧结构相同，因此不将MTU、分片、CRC、弱信号或跳包列为本次直接原因。
- [x] 写能力矩阵：`write=true`、两种写能力同时存在时显式响应写；仅无响应能力、混合缺失属性、`writeNoResponse=false` 且无明确响应写时升级前拒绝、两项属性缺失的 `legacy-unknown` 兼容，以及响应写 `10007` 后同帧一次回退。
- [x] 原生回调竞态：覆盖 `success→ACK`、`ACK→success`、`ACK→迟到fail`、`fail→无ACK`、无回调但有ACK；断言只有Boot ACK推进游标，迟到回调不影响新pending，300ms软超时不延长670ms总窗口。
- [x] 读取恢复：Android通知特征明确可读时450ms触发一次best-effort读取，669ms内读回ACK可结束请求；能力缺失/不支持/属性错误不探测，670ms仍无ACK只重发同一序号。iOS与MQTT/4G不得触发该读取。
- [x] 超时诊断：正常包仍维持单条ACK日志；重试/超时可区分原生success/fail/timeout、RX完全为空与收到但解析失败，不泄漏完整固件数据或挤掉会话头。
- [x] 已执行 `pnpm dlx tsx common/lib/bms-protocol/uni-ble-transport-ota.test.ts`、Boot时序/运行参数、页面OTA会话、BLE/MQTT transport及相关策略回归，并执行 `pnpm exec tsc --noEmit --pretty false` 与根仓/子仓 `git diff --check`；全部通过。
- [ ] 真机门槛保持不变：Android微信小程序/App三条BLE链路六组各连续成功20次、每组至少一次弱信号并核对版本；iOS BLE及4G/MQTT冒烟。若日志显示响应写原生成功但同包持续无RX，转交Bootloader落实Flash后ACK、重复包返回当前游标及完成ACK后重启，客户端不得继续盲目延时或跳包。
