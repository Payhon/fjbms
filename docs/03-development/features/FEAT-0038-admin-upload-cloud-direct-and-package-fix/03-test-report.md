# FEAT-0038 后台上传链路修复与云直传接入 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-04-09
- related_feature: FEAT-0038
- version: v0.1.0

## 1. 测试范围
- 后端文件类型校验白名单。
- 云直传凭证申请与登记前的统一文件校验。
- 共用上传器的进度展示与状态切换。
- 图片、安装包、升级文件的值回填语义。

## 2. 测试环境
- 工作区：`/Users/payhon/work2025/project/fjbms`
- 前端：`frontend/`
- 后端：`backend/`

## 3. 用例结果
- 已通过：`pnpm --dir frontend typecheck`
- 已通过：`go test ./pkg/utils ./internal/service -run TestValidateUploadBizType`
- 已通过：`bizType=appPackage` 接受 `.apk/.hap/.app`
- 已通过：`bizType=wgtPackage` 接受 `.wgt`
- 已通过：非法扩展名在本地上传、云凭证申请、云登记链路均返回校验失败
- 已通过：BMS OTA 升级包管理页“升级包固件”字段改为保存 `url`，避免提交 `./files-cloud/<id>` 导致后端创建升级包时读取本地文件失败
- 已通过：新增 OTA 升级包接口兼容云存储 CDN URL，签名计算支持远程下载流，不再将 `https://...` 当成本地文件路径打开
- 已通过：OTA 任务下发设备时，云存储升级包地址保持原始 CDN URL，不再额外拼接 `global.OtaAddress`
- 已通过：`go test ./internal/service -run TestSignPackageSource -count=1`
- 已通过：移动端头像上传优先使用 `/file/up` 返回的 `url`，不再将 `./files-cloud/<id>` 直接写入用户资料
- 已通过：`/api/v1/app/auth/profile`、`/api/v1/app/auth/wxmp/profile` 与 `/api/v1/user/detail` 兼容云存储头像路径归一化
- 待执行：云存储真实环境下浏览器直传回归，确认阿里云 / 七牛 CORS 配置完备
- 待执行：后台页面运行态确认上传过程中进度条与错误提示展示正常
- 待执行：移动端运行态回归头像上传后即时预览、刷新个人资料、重新登录后的头像显示

## 4. 缺陷与风险
- 云直传在真实环境中仍依赖对象存储桶跨域配置；若预检失败，前端会直接报错且不会回退本地上传。
- 本轮未覆盖所有零散上传页面，未接入共用上传器的页面仍沿用旧链路。

## 5. 结论
- 本次改动已通过静态与定向单测验证，具备提测条件，待运行态回归确认云直传环境配置。
