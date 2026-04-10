# FEAT-0038 后台上传链路修复与云直传接入 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-04-09
- related_feature: FEAT-0038
- version: v0.1.0

## 1. 方案概览
- 后端将文件扩展名校验从松散白名单改为按 `bizType` 明确分组，统一供本地上传、云直传凭证申请、云文件登记三条链路复用。
- 前端在共用上传层新增 `shared.ts` 上传适配器，统一执行“云直传优先，本地上传回退”的策略。
- 共用上传组件改用 `custom-request` 接管 Naive UI 默认上传实现，通过 `XMLHttpRequest` 获取稳定的进度回调。
- 页面层仅在安装包 / 升级文件等需要外链语义的字段上显式设置 `value-mode="url"`，不扩大影响范围。

## 2. 接口与数据结构
### 2.1 复用现有接口
- `POST /api/v1/file/up`
  - 本地存储上传与云存储未启用时的回退路径。
- `POST /api/v1/file/cloud/credential`
  - 获取云直传凭证。
- `POST /api/v1/file/cloud/register`
  - 云直传完成后登记文件元数据。

### 2.2 文件类型校验分组
- `image`: `.jpg/.jpeg/.png/.svg/.ico/.gif/.webp`
- `appPackage`: `.apk/.hap/.app`
- `wgtPackage`: `.wgt`
- `upgradePackage`: `.bin/.tar/.gz/.zip/.gzip/.apk/.dav/.pack`
- `importBatch`: `.xlsx/.xls/.csv`
- `d_plugin`: `.dpk`

### 2.3 前端上传适配器输入输出
- 输入：
  - `file: File`
  - `bizType?: string`
  - `onProgress?: (percent: number) => void`
  - `onStageChange?: (stage) => void`
- 输出：
  - 与现有上传接口一致的 `UploadRsp`，包含 `id/path/url` 等字段。

## 3. 关键流程
### 3.1 云直传优先
1. 前端先向 `/file/cloud/credential` 申请凭证。
2. 若成功：
   - 阿里云：使用返回的 `method/url/headers` 通过 `XMLHttpRequest` 直接 `PUT` 文件二进制。
   - 七牛云：使用返回的 `method/url/fields` 构造 `FormData`，通过 `XMLHttpRequest` 直接 `POST`。
3. 上传完成后调用 `/file/cloud/register`，获取最终 `UploadRsp`。

### 3.2 本地回退
1. 当 `/file/cloud/credential` 明确返回“未启用云存储”时，前端回退到 `/file/up`。
2. 本地上传同样使用 `XMLHttpRequest + FormData`，以保持进度条行为一致。

### 3.3 组件内状态管理
- 引入 `preparing/uploading/registering` 三阶段状态。
- 上传期间禁用打开弹窗、清空、移除、确认等破坏性操作。
- 在 `show-file-list=false` 场景下额外渲染独立进度条和状态文本。

## 4. 安全与权限
- 云直传 API 请求继续携带现有 `x-token` 与语言头，不改变鉴权模式。
- 后端在申请凭证和登记文件前都执行路径与扩展名校验，避免绕过本地上传的类型限制。
- 对象存储跨域和签名错误不做静默降级，直接暴露给用户，避免掩盖环境配置问题。

## 5. 测试策略
- 后端：
  - `ValidateFileType` 分组校验单测。
  - `validateUploadBizType` 覆盖合法与非法扩展名。
- 前端：
  - `pnpm --dir frontend typecheck`
  - 手工验证图片、安装包、升级文件在本地/云存储两种模式下的上传与回填行为。

## 6. 兼容性与迁移
- 不修改后端接口结构，无需数据库迁移。
- 已接入共用上传器的页面可直接获得直传能力；未接入页面维持原状。
- 对已有保存为内部路径的历史数据不做自动迁移，本次仅保证新上传值语义正确。
