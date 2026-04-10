# FEAT-0038 后台上传链路修复与云直传接入 - 功能规格

- status: review
- owner: payhon
- last_updated: 2026-04-09
- related_feature: FEAT-0038
- version: v0.1.0

## 1. 背景与目标
- 背景：
  - 后台共用上传器在云存储模式下仍通过业务服务器中转上传，无法直接复用对象存储原生上传能力。
  - 图片上传接口已返回可直接访问的 `url`，但部分页面上传链路仍依赖内部 `path`，导致前端回填地址错误。
  - `.apk` 等安装包上传会被后端文件类型校验拒绝，无法满足应用管理与升级发布场景。
  - 上传过程中缺少明确的组件内进度反馈，用户等待成本高，容易重复点击。
- 目标：
  1. 修复后端文件类型白名单，补齐 `appPackage` 与 `wgtPackage`。
  2. 为后台共用上传器接入云存储直传链路，并保留本地存储回退。
  3. 为共用上传器增加稳定的上传进度、状态与错误反馈。
  4. 明确图片与安装包场景的值回填语义，避免 `url/path` 串用。

## 2. 范围
### In Scope
- `backend/pkg/utils/file.go`
- `backend/internal/service/file.go`
- `backend/internal/service/file_validation_test.go`
- `frontend/src/components/business/file-picker/index.vue`
- `frontend/src/components/business/file-picker-multiple/index.vue`
- `frontend/src/components/business/image-upload/index.vue`
- `frontend/src/components/business/upload/shared.ts`
- `frontend/src/views/app_manage/apps/index.vue`
- `frontend/src/views/app_manage/upgrade/index.vue`
- FEAT-0038 文档与看板同步。

### Out of Scope
- 不改造仓库内所有零散手写 `NUpload` 页面。
- 不新增后端上传接口，不调整现有返回字段。
- 不处理对象存储桶的 CORS 配置，仅在前端暴露真实错误。

## 3. 用户价值
- 管理员在云存储模式下可以直接使用对象存储上传链路，减少中转路径。
- 图片、安装包、升级文件在后台表单中能拿到符合业务语义的 URL 或内部路径。
- 上传过程中可以看到明确进度与状态，避免误以为页面卡死。
- `.apk`、`.hap`、`.app`、`.wgt` 可按业务类型正常上传。

## 4. 验收标准
1. `bizType=appPackage` 时允许上传 `.apk/.hap/.app`，`bizType=wgtPackage` 时允许上传 `.wgt`。
2. 共用上传器在启用云存储时，请求链路为 `credential -> 供应商上传 -> register`。
3. 若云存储未启用，共用上传器自动回退到原 `/file/up`。
4. 上传过程中组件区域可见百分比进度与阶段状态文案，并在上传中禁用破坏性操作。
5. 图片类上传字段默认回填后端返回的 `url`，应用管理安装包与升级页安装包字段显式回填 `url`。
6. 本次改动通过 `pnpm --dir frontend typecheck` 与定向 `go test` 验证。

## 5. 风险与约束
- 云直传依赖 OSS / 七牛跨域配置，若部署环境未放行浏览器上传所需方法与请求头，将直接失败。
- 前端仅对“未启用云存储”这一类错误执行本地回退，其余云端配置或网络错误会按真实失败处理。
- 仓库中仍存在未接入共用上传器的页面，这些页面不会自动获得本次云直传能力。

## 6. 回滚方案
- 回滚共用上传器的自定义上传请求逻辑，恢复原 `/file/up` 中转上传。
- 回滚后端文件类型校验白名单调整。
- 回滚 FEAT-0038 文档与看板状态。
