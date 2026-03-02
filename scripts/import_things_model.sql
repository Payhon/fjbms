\if :{?json_payload}
\else
\echo 'ERROR: missing required psql variable: json_payload'
\echo 'Hint: pass it with -v json_payload="<compact-json>"'
\quit 1
\endif

BEGIN;

WITH payload AS (SELECT :'json_payload'::jsonb AS j),
ins AS (
  INSERT INTO device_templates
  SELECT *
  FROM jsonb_populate_recordset(
    NULL::device_templates,
    COALESCE((SELECT j -> 'device_templates' FROM payload), '[]'::jsonb)
  )
  ON CONFLICT DO NOTHING
  RETURNING 1
)
SELECT 'device_templates' AS table_name, COUNT(*) AS inserted_rows FROM ins;

WITH payload AS (SELECT :'json_payload'::jsonb AS j),
ins AS (
  INSERT INTO device_model_telemetry
  SELECT *
  FROM jsonb_populate_recordset(
    NULL::device_model_telemetry,
    COALESCE((SELECT j -> 'device_model_telemetry' FROM payload), '[]'::jsonb)
  )
  ON CONFLICT DO NOTHING
  RETURNING 1
)
SELECT 'device_model_telemetry' AS table_name, COUNT(*) AS inserted_rows FROM ins;

WITH payload AS (SELECT :'json_payload'::jsonb AS j),
ins AS (
  INSERT INTO device_model_attributes
  SELECT *
  FROM jsonb_populate_recordset(
    NULL::device_model_attributes,
    COALESCE((SELECT j -> 'device_model_attributes' FROM payload), '[]'::jsonb)
  )
  ON CONFLICT DO NOTHING
  RETURNING 1
)
SELECT 'device_model_attributes' AS table_name, COUNT(*) AS inserted_rows FROM ins;

WITH payload AS (SELECT :'json_payload'::jsonb AS j),
ins AS (
  INSERT INTO device_model_events
  SELECT *
  FROM jsonb_populate_recordset(
    NULL::device_model_events,
    COALESCE((SELECT j -> 'device_model_events' FROM payload), '[]'::jsonb)
  )
  ON CONFLICT DO NOTHING
  RETURNING 1
)
SELECT 'device_model_events' AS table_name, COUNT(*) AS inserted_rows FROM ins;

WITH payload AS (SELECT :'json_payload'::jsonb AS j),
ins AS (
  INSERT INTO device_model_commands
  SELECT *
  FROM jsonb_populate_recordset(
    NULL::device_model_commands,
    COALESCE((SELECT j -> 'device_model_commands' FROM payload), '[]'::jsonb)
  )
  ON CONFLICT DO NOTHING
  RETURNING 1
)
SELECT 'device_model_commands' AS table_name, COUNT(*) AS inserted_rows FROM ins;

COMMIT;
