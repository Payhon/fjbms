# FEAT-0027 后台删除终端用户后账号身份残留修复 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-03-26
- related_feature: FEAT-0027
- version: v0.1.0

## 1. 方案概览
问题根因分两部分：
- 新问题持续产生：后台删除用户调用 `dal.DeleteUsersById(id)`，只删除 `users` 记录，没有清理 `user_identities` 等关联表。
- 旧脏数据持续生效：注册/绑定查重逻辑优先读 `user_identities`，所以残留孤儿身份会一直阻塞新账号。

修复方案：
1. 抽取统一的用户级联清理函数，供“APP 自助注销”和“后台删用户”共用。
2. 后台删用户改为事务删除：先删关联数据，再删 `users`。
3. `dal.GetUserIdentity` 查询到身份后，再校验关联 `users` 是否存在；若用户已不存在，则自动删除该身份并按“未找到”返回。
4. 新增 `backend/sql/46.sql`，批量清理历史孤儿记录。

## 2. 影响表
- `users`
- `user_identities`
- `device_user_bindings`
- `app_device_added_records`
- `message_push_manage`
- `message_push_log`
- `user_roles`
- `user_address`

## 3. 关键流程
1. 后台执行删除用户。
2. 服务层读取目标用户并完成权限校验。
3. 开启事务，执行统一级联清理：
   - 删除 `user_identities`
   - 删除设备绑定/移动端添加记录
   - 删除推送记录、角色、地址
   - 最后删除 `users`
4. 后续注册/绑定流程查询身份时，若命中孤儿 `user_identities`，DAL 自动自修复并返回未找到。

## 4. 测试策略
- 定向 Go 测试/编译：
  - `backend/internal/dal`
  - `backend/internal/service`
  - `backend/internal/api`
- 手工验证：
  - 创建终端用户并绑定手机号/邮箱/微信
  - 后台删除用户
  - 重新注册并再次绑定，验证不再报“已被绑定”
- 数据修复验证：
  - 执行 `backend/sql/46.sql`
  - 抽样验证历史异常账号恢复正常

## 5. 兼容性与迁移
- 新逻辑不依赖前端改动。
- 需要在部署后执行 `backend/sql/46.sql`，修复历史孤儿数据。
- 若仅部署代码而未执行 SQL，旧脏数据中的 `user_identities` 可在再次命中查重时逐步自修复，但其它孤儿表仍会保留。
