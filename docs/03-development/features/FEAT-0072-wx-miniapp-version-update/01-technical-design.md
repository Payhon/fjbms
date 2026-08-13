# FEAT-0072 微信小程序版本更新检测 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-08-13
- related_feature: FEAT-0072
- version: v0.1.0

## 1. 方案概览

- 新增独立微信小程序更新控制器，封装 `wx.getUpdateManager()`。
- `App.vue.onLaunch` 仅在 `MP-WEIXIN` 下启动控制器；`onShow/onHide` 同步前后台可见状态。
- 控制器只负责微信小程序版本更新，不复用或修改 App 端 `fjbms-upgrade`。

## 2. 接口与状态

- 控制器公开：
  - `start()`：幂等注册 `onCheckForUpdate/onUpdateReady/onUpdateFailed`。
  - `onAppShow()`：标记前台，并在存在待应用更新时显示提示。
  - `onAppHide()`：标记后台，延迟更新提示。
- 内部状态：
  - `started`：防止重复注册监听器。
  - `appVisible`：避免后台弹窗。
  - `updateReady`：更新包已下载完成。
  - `promptVisible`：避免重复弹窗。
  - `applying`：防止重复执行 `applyUpdate()`。

## 3. 关键流程

1. 小程序启动取得微信 `UpdateManager` 并注册监听器。
2. `onCheckForUpdate` 仅记录平台返回结果；无更新时不提示。
3. `onUpdateReady` 设置待更新状态：
   - 当前前台：立即弹出不可取消提示；
   - 当前后台：等待下一次 `onAppShow`。
4. 用户确认后设置应用中状态并调用 `applyUpdate()`。
5. `onUpdateFailed` 清除待更新状态，并在前台显示下载失败提示。

## 4. 安全与权限

- 不请求额外用户权限，不访问业务后端，不读取或上传用户信息。
- 仅调用微信官方更新管理 API。
- 更新版本仍受微信公众平台审核、发布和灰度控制。

## 5. 测试策略

- 使用可注入的 UpdateManager、弹窗和翻译函数覆盖：幂等初始化、无更新不提示、前台更新、后台延迟提示、确认应用、下载失败。
- 执行 UniApp TypeScript 检查、更新控制器断言、`App.vue` SFC 脚本解析和差异检查。
- 通过微信开发者工具“模拟更新”或发布体验版/正式版完成运行时验收。

## 6. 兼容性与迁移

- 所有接入点使用 `MP-WEIXIN` 条件编译，Android/iOS App、H5 和其他小程序目标不加载该能力。
- 不新增服务端接口、存储字段或迁移脚本。
