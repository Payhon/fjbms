# FEAT-0038 后台上传链路修复与云直传接入 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-04-11 10:20
- related_feature: FEAT-0038
- version: v0.1.0

## 1. 实施记录
1. 排查后端上传链路，确认 `.apk` 被拒绝的根因是 `ValidateFileType` 仅覆盖图片、批量导入、升级包等少数场景，缺少 `appPackage` 与 `wgtPackage` 显式白名单。
2. 重构 `backend/pkg/utils/file.go` 文件类型白名单，改为按 `bizType` 明确分组。
3. 在 `backend/internal/service/file.go` 中新增统一的 `validateUploadBizType`，并接入 `UploadFile`、`CreateCloudUploadCredential`、`RegisterCloudFile`。
4. 新增 `backend/internal/service/file_validation_test.go`，覆盖 `appPackage`、`wgtPackage` 与非法扩展名场景。
5. 排查后台共用上传器，确认现有实现统一走 `/file/up`，无法使用云存储直传，也无法稳定拿到上传进度。
6. 新增 `frontend/src/components/business/upload/shared.ts`，统一封装云直传凭证申请、阿里云 / 七牛浏览器上传、文件登记与本地上传回退逻辑。
7. 将 `FilePicker`、`FilePickerMultiple`、`ImageUpload` 改为 `custom-request` 模式，使用组件内进度状态代替原 `finish` 事件串联。
8. 在三个共用上传组件中增加上传阶段文案、百分比进度条、错误提示，并在上传期间禁用打开、清空、删除、确认等动作。
9. 在应用管理与升级发布页面为安装包类字段显式设置 `value-mode="url"`，保证业务字段保存外链下载地址。
10. 根据运行态反馈继续排查 BMS OTA 升级包管理页，确认“升级包固件”字段仍显式配置为 `value-mode="path"`，导致云存储上传后 `package_url` 提交了 `./files-cloud/<id>` 而不是 CDN URL。
11. 将 `frontend/src/views/bms/battery/ota/package/index.vue` 的“升级包固件”选择器改为 `value-mode="url"`，使 OTA 包管理在云存储模式下提交可直接访问的升级包地址。
12. 根据新增接口报错继续排查后端 OTA 服务，确认 `CreateOTAUpgradePackage` / `UpdateOTAUpgradePackage` 在生成签名时仍将 `package_url` 当作本地文件路径打开，无法兼容云存储 CDN URL。
13. 在 `backend/internal/service/ota.go` 中新增“本地路径 / HTTP(S) URL 双模式签名”能力，云存储场景改为下载文件流后计算 MD5 / SHA256。
14. 同步修正 OTA 任务下发给设备时的升级包地址生成逻辑，云存储 URL 不再错误拼接 `global.OtaAddress`。
15. 新增 `backend/internal/service/ota_sign_test.go`，覆盖本地文件与远程 URL 两种签名计算场景。
16. 根据移动端反馈继续排查头像更新链路，确认 UniApp 设置页上传头像时仍只消费 `/file/up` 返回的 `path`，而 `AppAuth.UpdateProfile` 与 `/user/detail` 也未对 `./files-cloud/<id>` 做云存储 URL 归一化。
17. 在 `backend/internal/service/file.go` 新增 `resolveStoredFileURL`，可将 `./files-cloud/<id>` 解析为 `files.full_url`。
18. 在 `backend/internal/service/app_auth.go` 中将 `UpdateProfile`、`WxmpUpdateProfile` 接收到的 `avatar_url` 统一归一化后再落库，兼容旧客户端仍提交内部路径的情况。
19. 在 `backend/internal/service/sys_user.go` 的 `GetUserDetail` 中对 `avatar_url` 做返回前归一化，兼容历史已存储为 `./files-cloud/...` 的头像数据。
20. 在 `fjbms-uniapp/pages/my/setting/index.vue` 中将头像上传结果改为优先取后端返回的 `url`，仅在缺失时回退 `path`。
21. 执行 `gofmt`、后端定向 `go test` 与 UniApp TypeScript 校验验证通过。

## 2. 待执行项
- 在运行环境验证 OSS / 七牛跨域配置是否允许浏览器直传。
- 结合真实页面验证 `credential -> provider upload -> register` 请求序列。

## 3. 当前状态
- 代码、静态验证、文档与看板已同步，当前处于提测状态。
