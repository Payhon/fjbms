# FEAT-0027 后台删除终端用户后账号身份残留修复 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-03-26
- related_feature: FEAT-0027
- version: v0.1.0

## 1. 实施记录
1. 新建 FEAT-0027 文档目录，并在项目看板登记 Backend 条目。
2. 新增 `backend/internal/service/user_cleanup.go`，统一封装用户级联清理逻辑。
3. 将 `AppAuth.DeleteAccount` 改为复用统一清理逻辑，避免自助注销与后台删除两套实现分叉。
4. 将后台 `User.DeleteUser` 改为事务删除，并同步清理 `user_identities`、绑定记录、地址、角色等关联数据。
5. 为 `backend/internal/dal/user_identities.go` 增加孤儿身份自修复：身份存在但用户不存在时，自动删除残留身份并按未找到返回。
6. 新增 `backend/sql/46.sql`，用于一次性清理线上历史孤儿身份/绑定数据。

## 2. 当前状态
- 后端代码已完成。
- SQL 修复脚本已补齐。
- 已完成定向 Go 校验，待测试环境执行 SQL 并回归验证后台删除/重新注册/重新绑定链路。
