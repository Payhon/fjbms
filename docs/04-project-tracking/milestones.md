# 里程碑计划

## M0
- FEAT-0001：文档治理体系建立（完成）

## M1
- FEAT-0002：历史文档迁移与分层重构（完成）
- FEAT-0004：电池/MES 对接统一鉴权与审计日志
- FEAT-0005：管理端设备详情页字段对齐（MES 扩展字段）
- FEAT-0006：UniApp 升级检测与提示体验优化

## 历史开发进度（迁移）

- source: `doc/开发进度.md`
- last_updated: 2026-02-14

**日期**: 2025-12-03 10:00  
**阶段**: 第一阶段 - BMS 后端开发（已完成）

---

## ✅ 已完成工作

### 1. 数据库层 (100%)
- [x] 数据库迁移脚本 `backend/sql/13.sql`
  - 6张新表创建
  - 索引优化
  - 外键关系定义

### 2. 模型层 (100%)
- [x] GORM 模型文件 (6个)
  - dealers.gen.go
  - battery_models.gen.go
  - device_batteries.gen.go
  - device_transfers.gen.go
  - device_user_bindings.gen.go
  - warranty_applications.gen.go

- [x] HTTP 请求/响应模型 (5个)
  - dealers.http.go
  - battery_models.http.go
  - device_transfers.http.go
  - device_user_bindings.http.go
  - warranty_applications.http.go

### 3. Service 层 (100%)
- [x] `backend/internal/service/dealer.go` - 经销商管理服务
  - CreateDealer - 创建经销商
  - UpdateDealer - 更新经销商
  - DeleteDealer - 删除经销商 (含业务校验)
  - GetDealerByID - 获取详情
  - GetDealerList - 分页列表

- [x] `backend/internal/service/battery_model.go` - 电池型号管理服务
  - CreateBatteryModel - 创建型号
  - UpdateBatteryModel - 更新型号
  - DeleteBatteryModel - 删除型号 (含业务校验)
  - GetBatteryModelByID - 获取详情
  - GetBatteryModelList - 分页列表

- [x] `backend/internal/service/device_transfer.go` - 设备转移服务
  - TransferDevices - 批量转移设备（含事务）
  - GetTransferHistory - 转移记录查询（关联设备、经销商、操作人）

- [x] `backend/internal/service/device_binding.go` - 设备绑定服务（APP 激活）
  - BindDevice - 绑定设备（校验序列号/密钥、写入 device_user_bindings、更新激活状态）
  - UnbindDevice - 解绑设备（删除绑定关系、必要时重置激活状态）
  - GetUserDevices - 获取用户绑定设备列表

- [x] `backend/internal/service/warranty.go` - 维保管理服务
  - CreateWarrantyApplication - 创建维保申请
  - UpdateWarrantyStatus - 更新申请状态及处理结果
  - GetWarrantyList - 维保申请列表查询
  - GetWarrantyDetail - 维保申请详情

### 4. API 层与路由 (100%)
- [x] 新增 API 文件
  - `backend/internal/api/dealer.go`
  - `backend/internal/api/battery_model.go`
  - `backend/internal/api/device_transfer.go`
  - `backend/internal/api/device_binding.go`
  - `backend/internal/api/warranty.go`
- [x] 路由注册
  - `backend/router/apps/dealer.go`
  - `backend/router/apps/battery_model.go`
  - `backend/router/apps/device_transfer.go`
  - `backend/router/apps/device_binding.go`
  - `backend/router/apps/warranty.go`
  - 在 `backend/router/router_init.go` 中挂载至 `/api/v1` 下 BMS 分组
- [x] 数据权限中间件
  - `backend/internal/middleware/dealer_auth.go` - DealerAuthMiddleware
  - 在 BMS 路由分组上挂载，提供 `dealer_id` 上下文

## 📋 下一步计划

### 近期工作（当前优先）
1. ✅ 整理 BMS 模块后端完成报告与测试用例文档
2. ✅ 为 BMS Web 管理端补充“维保中心”页面与菜单
3. ⏳ 编写/完善 Swagger 文档（覆盖 BMS 新增接口）
4. ⏳ 补充后端集成测试/单元测试（重点覆盖设备转移、绑定、维保流程）

### 后续任务
1. Web 端：BMS Dashboard、电池列表/生命周期视图
2. APP 端：扫码绑定、设备详情页、维保申请入口对接
3. 性能与安全性评估（大规模经销商/设备场景）

---

## 💡 技术要点

### Service 层设计原则
1. **事务处理**: 涉及多表操作使用事务
2. **权限校验**: 所有操作验证 tenant_id
3. **业务校验**: 删除前检查关联数据
4. **错误处理**: 统一使用 errcode 包装错误

### 代码示例
```go
// 事务示例
tx := query.Use(global.DB).Begin()
defer func() {
    if r := recover(); r != nil {
        tx.Rollback()
    }
}()

// 操作1
if err := tx.DeviceBattery.Create(...); err != nil {
    tx.Rollback()
    return err
}

// 操作2
if err := tx.DeviceTransfer.Create(...); err != nil {
    tx.Rollback()
    return err
}

tx.Commit()
```

---

**状态**: 🟢 第一阶段（BMS 后端）已完成  
**下一步**: 扩展 Swagger / 测试用例，并推进 Web & APP 端功能开发
