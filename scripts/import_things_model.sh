#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JSON_FILE="${ROOT_DIR}/doc/things_model.json"
SQL_FILE="${ROOT_DIR}/scripts/import_things_model.sql"

TENANT_ID="${TENANT_ID:-}"
TEMPLATE_ID="${TEMPLATE_ID:-}"
DATABASE_URL="${DATABASE_URL:-}"

usage() {
  cat <<'EOF'
Usage:
  scripts/import_things_model.sh --db-url <postgresql-url> [options]

Options:
  --db-url <url>         PostgreSQL URL, for example:
                         postgresql://postgres:postgres@127.0.0.1:5432/ThingsPanel?sslmode=disable
  --json-file <path>     JSON file path (default: doc/things_model.json)
  --tenant-id <id>       Replace "{{TENANT_ID}}" placeholder in JSON
  --template-id <id>     Override template id in JSON (optional)
  -h, --help             Show this help

Environment fallback:
  DATABASE_URL           same as --db-url
  TENANT_ID              same as --tenant-id
  TEMPLATE_ID            same as --template-id
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --db-url)
      DATABASE_URL="${2:-}"
      shift 2
      ;;
    --json-file)
      JSON_FILE="${2:-}"
      shift 2
      ;;
    --tenant-id)
      TENANT_ID="${2:-}"
      shift 2
      ;;
    --template-id)
      TEMPLATE_ID="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "${DATABASE_URL}" ]]; then
  echo "ERROR: --db-url is required (or set DATABASE_URL)." >&2
  exit 1
fi

if [[ ! -f "${JSON_FILE}" ]]; then
  echo "ERROR: JSON file not found: ${JSON_FILE}" >&2
  exit 1
fi

if [[ ! -f "${SQL_FILE}" ]]; then
  echo "ERROR: SQL file not found: ${SQL_FILE}" >&2
  exit 1
fi

JSON_PAYLOAD="$(
python3 - "${JSON_FILE}" "${TENANT_ID}" "${TEMPLATE_ID}" <<'PY'
import json
import sys
from typing import Any

json_file = sys.argv[1]
tenant_id = sys.argv[2]
template_id = sys.argv[3]

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

old_template_id = (
    (data.get("meta") or {})
    .get("placeholders", {})
    .get("device_template_id")
)

def walk_replace(v: Any) -> Any:
    if isinstance(v, dict):
        return {k: walk_replace(x) for k, x in v.items()}
    if isinstance(v, list):
        return [walk_replace(x) for x in v]
    if isinstance(v, str):
        if tenant_id and v == "{{TENANT_ID}}":
            return tenant_id
        if template_id and old_template_id and v == old_template_id:
            return template_id
    return v

data = walk_replace(data)

def has_tenant_placeholder(v: Any) -> bool:
    if isinstance(v, dict):
        return any(has_tenant_placeholder(x) for x in v.values())
    if isinstance(v, list):
        return any(has_tenant_placeholder(x) for x in v)
    return isinstance(v, str) and v == "{{TENANT_ID}}"

if has_tenant_placeholder(data):
    raise SystemExit(
        "ERROR: unresolved placeholder '{{TENANT_ID}}'. Please pass --tenant-id."
    )

print(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
PY
)"

echo "Importing things model JSON from: ${JSON_FILE}"
if [[ -n "${TENANT_ID}" ]]; then
  echo "Using tenant_id: ${TENANT_ID}"
fi
if [[ -n "${TEMPLATE_ID}" ]]; then
  echo "Overriding template_id: ${TEMPLATE_ID}"
fi

psql "${DATABASE_URL}" \
  -v ON_ERROR_STOP=1 \
  -v json_payload="${JSON_PAYLOAD}" \
  -f "${SQL_FILE}"

echo "Done."
