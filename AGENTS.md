# Repository Guidelines

## Project Structure & Module Organization

This repository is a multi-module project:

- `backend/`: Go API service (entrypoint `main.go`). Key areas: `internal/` (app code), `router/` (HTTP routes), `configs/` (YAML config), `sql/` (schema/migrations), `static/` (static assets), `test/` (Go tests + DB bootstrap helpers).
- `frontend/`: Vue 3 + Vite web app (admin/tenant UI). Main code in `src/`, static files in `public/`, shared workspace packages in `packages/`.
- `fjbms-uniapp/`: Uni-app mobile client. Pages in `pages/`, shared code in `common/`, components in `components/`, assets in `static/`.
- `docs/`: Primary documentation workspace (governance, product, architecture, development, tracking, operations).
- `doc/`: Legacy documentation archive (historical copies, no longer the primary authoring location).

## Build, Test, and Development Commands

Backend:

- `cd backend && go run .` — run the API locally (Swagger typically at `http://localhost:9999/swagger/index.html`).
- `cd backend && go test ./...` — run Go unit tests.

Frontend:

- `cd frontend && pnpm install` — install dependencies (pnpm workspace).
- `cd frontend && pnpm dev` — start Vite dev server.
- `cd frontend && pnpm build` — production build (includes `typecheck`).
- `cd frontend && pnpm lint` / `pnpm format` — ESLint auto-fix and Prettier formatting.
- `cd frontend && pnpm quality-check` — pre-commit quality gate used by hooks.

## Coding Style & Naming Conventions

- Go: format with `gofmt`; keep packages small; exported identifiers use `PascalCase`.
- Frontend: 2-space indentation (see `frontend/.editorconfig`); TypeScript + Vue SFC; keep formatting/lint clean via Prettier/ESLint.
- Follow existing naming patterns in the directory you’re editing; avoid large renames.
- **Database inserts (PostgreSQL/GORM):** avoid `db.Table(...).Create(map[string]any{...})` — this can trigger `LastInsertId` (unsupported by the PG driver). Prefer struct-based `Create(&row)` or model-based inserts.

## Testing Guidelines

- Backend tests use Go’s `testing` package (`*_test.go`). Some DB-oriented tests under `backend/test/` expect a local config like `backend/configs/conf-localdev.yml` (copy from `conf-dev.yml` and adjust credentials) and are commonly run with `run_env=localdev go test -v ./...`.
- Frontend currently relies on `pnpm typecheck` + `pnpm lint` and manual UI verification (include repro steps/screenshots in PRs for visual changes).

## Commit & Pull Request Guidelines

- Use Conventional Commits (observed in history): `feat: ...`, `fix: ...`, `docs: ...`, `chore(scope): ...`.
- PRs: include a short summary, linked issue/task (if any), test commands run (and results), and screenshots/GIFs for UI changes.

## Security & Configuration Tips

- Don’t commit secrets (DB passwords, API keys). Prefer local-only `.env*` (frontend) and `backend/configs/*` overrides.
- If you add new config keys, document defaults in `docs/` and keep backwards compatibility where possible.

## Device Type Rules

- BLE 设备类型通过 MAC 首字节区分：`0xAA` 为 BMS 仪表设备，`0xAC` 为 BMS 电池设备。
- 涉及 OTA/协议地址选择时必须先判定设备类型；仪表设备的 OTA 目标地址使用 `0xFC`。

<!-- DOC_GOVERNANCE_START -->
## 文档治理（强制）

### 1) 文档优先原则
1. 无功能规格文档（`00-feature-spec.md`）不得开始编码。
2. 文档是开发入口，不是附属品。
3. 开发完成必须回写文档并更新看板。

### 2) 文档根目录与层级
- 根目录固定：`docs/`
- 目录和模板遵循：`docs/00-governance/` 与 `docs/00-governance/templates/`
- 功能文档路径：`docs/03-development/features/FEAT-xxxx-<slug>/`

### 3) 文档生命周期
`draft -> approved -> in_progress -> review -> done -> archived`

### 4) 文档新增触发条件
- 新功能开发
- 重大重构
- 安全策略变更
- 对外接口/协议变更

### 5) 文档更新触发条件
- 实现方案变更
- 数据结构或接口字段变更
- 测试结果变化
- 发布范围或回滚策略变化
- 看板状态变化

### 6) 命名规范
- 功能编号：`FEAT-xxxx`
- 功能目录：`FEAT-xxxx-<slug>`（kebab-case）
- 固定文件顺序：`00-feature-spec.md`、`01-technical-design.md`、`02-implementation-log.md`、`03-test-report.md`、`04-release-note.md`

### 7) 责任人规范
- 每个功能文档必须标注 `owner`。
- 责任人负责文档与实现一致性。

### 8) 验收规范（DoD）
功能标记完成前必须同时满足：代码、测试、文档、看板四项同步完成。

### 9) PR/提交检查项（必须包含）
- [ ] 文档已新增/更新（如适用）
- [ ] `board.md` 状态已同步
- [ ] 风险与回滚说明已更新

### 10) 语言规范
- 文档默认中文。
- 必要术语可中英并列。
<!-- DOC_GOVERNANCE_END -->
