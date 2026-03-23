# FEAT-0024 item_uuid 大小写归一化防重复注册 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-03-23
- related_feature: FEAT-0024

## 已执行
- `backend`: `go test ./internal/service ./internal/api ./internal/model`
  - 结果：通过
  - 备注：存在第三方依赖 `gopsutil/disk` 的 macOS deprecation warning，不影响测试通过
- `fjbms-uniapp`: `pnpm exec tsc -p tsconfig.json --noEmit`
  - 结果：通过

## 待真机回归
- 读取小写 UUID 的 BLE 开通流程命中已有大写设备
- 大写 UUID 扫码绑定流程保持不变
- 遗留设备自动补建写入大写 `item_uuid`
