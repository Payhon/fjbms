# FEAT-0043 UniApp 头像展示与裁切优化 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-17
- related_feature: FEAT-0043
- version: v0.1.0

## 1. 设计概述
- 抽出 `common/avatar.ts` 统一封装默认头像与头像 URL 解析，兼容绝对 URL、`serverAddress` 基址和历史相对路径。
- 新增 `components/app-avatar/app-avatar.vue` 作为轻量头像展示组件，统一容器裁剪、圆角形态和图片填充模式。
- 设置页复用现有 `u-cropper` 组件，通过页面层编排实现“先选图，再载入裁切器，再上传保存”。

## 2. 数据与接口
### 2.1 头像展示
- 输入：`userStore.userInfo.avatar_url`
- 处理：
  - 若为空，返回默认头像。
  - 若为绝对 URL / data URL，直接返回。
  - 若为相对路径，则按 `getBaseUrl()` 或本地 `serverAddress` 去除 `/api/v1` 后拼接访问地址。
- 输出：页面统一使用解析后的 `avatarSrc`。

### 2.2 裁切与保存
1. 设置页点击“修改头像”。
2. 调用 `uni.chooseImage` 允许相册/拍照单图选择。
3. 将所选图片路径传给 `u-cropper.loadImage`。
4. 用户在裁切器内拖拽、缩放、旋转并确认。
5. 页面收到裁切后的临时文件路径，调用现有 `uploadOne` 上传。
6. 上传成功后继续请求 `POST /api/v1/app/auth/profile` 保存 `avatar_url`。
7. 保存成功后更新 `userStore` 并重新拉取 `/api/v1/user/detail`。

## 3. 关键实现点
- `pages/my/my.vue`
  - 改为使用统一头像组件，去掉页面内分散的头像默认值/路径拼接逻辑。
- `pages/my/setting/index.vue`
  - 右侧头像改为统一头像组件。
  - `handleEditAvatar` 改为选图后打开裁切流程，不再直接上传。
  - 裁切组件仅服务设置页头像修改；微信 `u-wx-auth` 仍只保留原授权链路。
- `lang/*`
  - 新增头像选择失败、裁切失败、保存中等文案。

## 4. 兼容性说明
- 不改接口字段，不增加新的后端依赖。
- 微信小程序授权头像/昵称更新逻辑保持原样，避免把本次裁切范围扩大到授权资料链路。
- 裁切结果输出为正方形头像图，展示层仍以圆形容器为主。
