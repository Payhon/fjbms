# Repository Guidelines

## Project Structure & Module Organization

This repository is a multi-module project:

- `backend/`: Go API service (entrypoint `main.go`). Key areas: `internal/` (app code), `router/` (HTTP routes), `configs/` (YAML config), `sql/` (schema/migrations), `static/` (static assets), `test/` (Go tests + DB bootstrap helpers).
- `frontend/`: Vue 3 + Vite web app (admin/tenant UI). Main code in `src/`, static files in `public/`, shared workspace packages in `packages/`.
- `fjbms-uniapp/`: Uni-app mobile client. Pages in `pages/`, shared code in `common/`, components in `components/`, assets in `static/`.
- `doc/`: Project documentation (architecture, dev guides, DB docs).

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

## Testing Guidelines

- Backend tests use Go’s `testing` package (`*_test.go`). Some DB-oriented tests under `backend/test/` expect a local config like `backend/configs/conf-localdev.yml` (copy from `conf-dev.yml` and adjust credentials) and are commonly run with `run_env=localdev go test -v ./...`.
- Frontend currently relies on `pnpm typecheck` + `pnpm lint` and manual UI verification (include repro steps/screenshots in PRs for visual changes).

## Commit & Pull Request Guidelines

- Use Conventional Commits (observed in history): `feat: ...`, `fix: ...`, `docs: ...`, `chore(scope): ...`.
- PRs: include a short summary, linked issue/task (if any), test commands run (and results), and screenshots/GIFs for UI changes.

## Security & Configuration Tips

- Don’t commit secrets (DB passwords, API keys). Prefer local-only `.env*` (frontend) and `backend/configs/*` overrides.
- If you add new config keys, document defaults in `doc/` and keep backwards compatibility where possible.
