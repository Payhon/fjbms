# FEAT-0032 UniApp 开发者模式 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-03
- related_feature: FEAT-0032
- version: v0.1.0

## 1. 方案概览
- 状态层：
  - 新增 `useDeveloperStore()`，维护 `enabled` 布尔值。
  - 状态初始化时读取本地存储，开启后写回本地存储，实现跨页面、跨重启持久化。
- 运行时信息层：
  - 新增统一调试信息读取工具，输出 `baseVersion`、`appVersion`、`apiBaseUrl`。
  - `apiBaseUrl` 直接复用现有 `resolveBaseUrl()`，确保与真实请求一致。
  - 版本号优先读取 `uni.getAppBaseInfo()` / `uni.getSystemInfoSync()`，APP 场景下再用 `plus.runtime` 补齐兜底。
- 页面层：
  - 登录页顶部 LOGO 增加点击计数，单次点击间隔超过 1.5 秒则重置。
  - 达到 9 次后开启开发者模式。
  - 登录卡片底部在 `enabled=true` 时展示调试信息块。

## 2. 接口与数据结构
- 本次不新增后端接口。
- 新增前端调试信息结构：
  - `baseVersion: string`
  - `appVersion: string`
  - `apiBaseUrl: string`
- 新增本地存储键：
  - `__developer_mode_enabled__`

## 3. 关键流程
1. 用户进入登录页，开发者模式默认从本地存储恢复。
2. 用户连续点击顶部 LOGO，页面累加点击次数。
3. 若任意两次点击间隔超过 1.5 秒，则点击计数清零并重新开始。
4. 达到第 9 次时，设置 `developerStore.enabled = true`，并写回本地存储。
5. 页面读取当前运行时调试信息，在登录卡片底部展示版本号与 API BaseURL。
6. 后续其他页面可通过同一 store 直接读取开发者模式状态。

## 4. 安全与权限
- 开发者模式仅影响前端展示，不提升账号权限，不绕过认证，不改变接口参数。
- 调试信息仅展示客户端本地已有的版本与接口地址，不新增敏感数据暴露面。
- BaseURL 展示遵循当前运行时实际解析结果，避免展示与真实请求不一致的静态地址。

## 5. 测试策略
- 静态校验：
  - `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
- 交互验证：
  - 登录页普通点击 LOGO 不应误触发开发者模式。
  - 连续点击 9 次后显示提示，并在卡片底部出现调试信息。
  - 页面重进后开发者模式状态仍保留。
  - APP / 小程序 / H5 等版本字段缺失场景下页面不报错。
- 回归验证：
  - 登录、注册、忘记密码、验证码刷新、微信登录展示逻辑不受影响。

## 6. 兼容性与迁移
- 不涉及 SQL、接口协议或现有数据模型迁移。
- 版本号获取逻辑允许字段为空，统一回退为 `--`，保证旧平台兼容。
- 对旧代码的兼容策略：
  - 在 legacy `$store.state` 中补充 `developerMode` 字段，便于历史页面后续按需读取。
