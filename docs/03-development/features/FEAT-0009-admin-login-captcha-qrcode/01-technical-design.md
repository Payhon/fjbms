# FEAT-0009 管理端登录验证码与二维码配置展示 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-06
- related_feature: FEAT-0009
- version: v0.1.0

## 1. 方案概览
- 后端新增登录验证码接口：生成随机码 + SVG 图片，写入 Redis（短 TTL）。
- 登录接口扩展：请求体新增 `captcha_id`、`captcha_code`，登录前执行验证码校验并一次性消费。
- 主题设置扩展：`logo` 表新增二维码字段，沿用当前主题设置 API（`/api/v1/logo`）读写。
- 前端改造：
  - 密码登录表单新增验证码输入 + 验证码图片点击刷新。
  - 主题设置页新增两个图片上传项。
  - 登录页新增二维码展示区并按配置动态渲染。

## 2. 接口与数据结构
- `GET /api/v1/login/captcha`
  - 返回：`{ captcha_id: string, captcha_image: string, expires_in: number }`
  - `captcha_image` 使用 `data:image/svg+xml;base64,...`。
- `POST /api/v1/login`
  - 入参扩展：`captcha_id`、`captcha_code`（必填）。
- `logo` 配置扩展字段：
  - `wxmp_qrcode`：微信小程序二维码路径
  - `app_download_qrcode`：App 下载页二维码路径

## 3. 关键流程
1. 获取验证码：前端请求 `/login/captcha`，展示图片和 `captcha_id`。
2. 登录校验：提交账号密码 + 验证码；后端比对 Redis 中验证码（大小写不敏感），验证后删除。
3. 主题配置：管理员上传二维码图片并保存到 `logo`。
4. 登录展示：系统设置 Store 初始化时读取二维码地址并转换为可访问 URL，登录页展示。

## 4. 安全与权限
- 验证码 TTL 默认 5 分钟，避免长期有效。
- 验证码校验失败后同样消费，减少重放尝试。
- 主题配置接口仍走现有权限（系统设置管理权限）。

## 5. 测试策略
- 后端：
  - 编译与单测（重点验证登录链路编译通过）。
- 前端：
  - `pnpm typecheck` + `pnpm lint`。
  - 手工验证登录验证码流程、二维码上传与登录页展示。

## 6. 兼容性与迁移
- 数据库通过增量 SQL 迁移新增列，默认空字符串，兼容历史数据。
- 登录请求新增验证码字段后，管理端前端同步升级即可；APP/小程序认证接口不受影响。
