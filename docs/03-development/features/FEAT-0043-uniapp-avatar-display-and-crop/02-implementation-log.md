# FEAT-0043 UniApp 头像展示与裁切优化 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-17 17:20
- related_feature: FEAT-0043
- version: v0.1.0

## 1. 实施记录
1. 排查 `pages/my/my.vue` 与 `pages/my/setting/index.vue`，确认头像展示逻辑分散，且设置页头像修改为“选图后直传”。
2. 复查 FEAT-0038 头像链路修复记录，明确本次必须兼容云存储 URL 与历史相对路径。
3. 新增 `fjbms-uniapp/common/avatar.ts`，统一默认头像与头像 URL 解析逻辑。
4. 新增 `fjbms-uniapp/components/app-avatar/app-avatar.vue`，统一头像容器裁剪与 `aspectFill` 展示。
5. 将“我的”页头像替换为统一头像组件，确保圆形容器内始终居中展示。
6. 将设置页右侧头像替换为统一头像组件，与“我的”页共享同一数据源和回退口径。
7. 在设置页接入 `u-cropper`，改造 `handleEditAvatar` 为“相册/拍照选图 -> 裁切 -> 上传 -> 保存资料”。
8. 保留 `u-wx-auth` 原有授权头像/昵称更新链路，不将本次裁切范围扩展到微信授权资料更新。
9. 补齐中英文头像裁切相关提示文案。
10. 新增 FEAT-0043 文档并更新看板。
11. 根据安卓联调反馈继续排查头像裁切运行态，确认 `u-cropper` 内部存在 `uni.$u.t(...)` 调用错误，点确认时会直接抛出 `TypeError: uni.$u.t is not a function`。
12. 修复 `u-cropper` 的错误提示调用口径，并补充“裁切器未初始化时先缓存待加载图片、初始化完成后再加载”的时序保护，避免设置页从相册/拍照进入裁切界面后出现空白图。
13. 设置页头像裁切流程改为等待裁切器 `open` 事件后再注入图片路径，和组件内部延迟加载保护形成双保险，降低 Android 拍照回调后空白或流程中断风险。
14. 根据最新 Android 真机反馈继续排查拍照后闪退问题，确认头像入口此前直接使用 `chooseImage` 取相机图片并把结果原样送入裁切器，和项目现有 `u-upload` 在 APP 端改用 `chooseMedia` 的策略不一致。
15. 将头像入口在 `APP-PLUS` 下切换为 `chooseMedia` 取图，并在进入裁切器前追加一次 `compressImage` 预压缩，优先收敛相机返回大图导致的内存压力和路径兼容风险。
16. 进一步将“拍照”和“从相册选择”拆成两条显式入口，避免 Android 在混合 `sourceType` 选择器里走拍照分支时出现不稳定行为；同时补充头像拍照链路的关键日志，便于继续跟踪崩溃发生在取图、压缩还是裁切器打开阶段。
17. 根据测试反馈补充 `u-cropper` 双指缩放能力：裁切器底层触摸逻辑从仅单指拖拽扩展为支持双指缩放，并以双指中心为缩放锚点，保留原有边界约束。
18. 排查启动期 `getApp() failed` 告警，确认根因是 `lang/index.ts` 在模块初始化阶段过早调用 `uni.setLocale`；已改为在 `main.ts createApp()` 完成 `app.use(i18n)` 后再同步 uni 内置 locale，避免启动阶段触发无意义告警。
19. 根据最新安卓日志确认拍照链路在 `[avatar] compress start` 后直接闪退，崩溃点落在原生 `uni.compressImage`；因此撤销 APP 端头像拍照后的二次压缩，直接复用 `chooseMedia + sizeType=compressed` 已返回的压缩图。
20. 将 locale 同步时机再后移到 `App.vue onLaunch`，避免 `main.ts` 阶段仍然过早触发 uni 内置 `getApp()` 路径。
21. 根据继续复现的安卓日志确认崩溃发生在裁切器 `loadImage` 之后，进一步将 `u-cropper` 底层图片源统一做 APP 本地路径标准化：`file:///...` 去掉 scheme，`_doc/...` 等路径通过 `plus.io.convertLocalFileSystemURL` 转换后再交给 `uni.getImageInfo`。

## 2. 待执行项
- 运行 `pnpm exec tsc --noEmit` 验证 UniApp 类型与模板编译。
- 手工回归“我的”页与设置页头像展示，以及裁切后的头像上传保存链路。

## 3. 当前状态
- 代码与文档已同步，等待静态校验与运行态验收结论。
