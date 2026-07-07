# FEAT-0064 移动端与 Web BMS 展示修正 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-07-07
- related_feature: FEAT-0064
- version: v0.1.0

## 1. 方案概览
- UniApp 在 `common/wxmp-runtime.ts` 增加默认品牌图使用判断，仅明确普通租户小程序允许回退默认富嘉图。
- 首页和登录页保持小程序初始图片为空，运行配置返回后按专属图优先、明确普通租户兜底、其他场景空白处理。
- 保护状态列表继续使用现有 i18n key，只将 key 的值改为 `ON/OFF`。
- Web 电芯电压值移除竖排和旋转样式，改为横向居中单行。

## 2. 接口与数据结构
- 不新增后端接口。
- 不新增数据库字段。
- 不改变 `/api/v1/app/wxmp/runtime` 返回结构。
- 前端新增 `shouldUseDefaultWxmpBrandAsset(config)`，判断条件为 `login_only === false` 且 `source_type === 'TENANT'`。

## 3. 关键流程
1. 微信小程序进入首页或登录页时，Banner/Logo 初始为空。
2. 调用运行配置接口后，若返回专属图片 URL，直接展示专属图片。
3. 若无专属图片，只有明确普通租户小程序才展示默认富嘉图。
4. PACK、配置加载失败、未返回 runtime 或字段缺失时保持空白。
5. Web BMS 面板电芯列表仍使用原电压数据和滚动容器，只改变数值文本 CSS。

## 4. 安全与权限
- 不修改登录、账号、组织、权限和小程序配置保存逻辑。
- PACK 判定仍消费服务端运行配置返回，不新增客户端硬编码 AppID。

## 5. 测试策略
- UniApp 执行 TypeScript 静态校验与子仓空白检查。
- Web 执行 TypeScript 校验和 BMS 面板文件 targeted ESLint。
- 文档和看板执行空白检查。
- PACK 小程序、普通租户小程序、Web BMS 面板由目标运行环境补充手工回归。

## 6. 兼容性与迁移
- APP 和 H5 端继续使用原默认图策略，不受小程序条件编译外逻辑影响。
- 普通租户小程序保持原默认图兜底能力。
- 不需要 SQL、后端发布或数据迁移。
