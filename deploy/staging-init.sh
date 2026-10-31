#!/bin/sh
# Runs only in a fresh disposable PostgreSQL container; never mount on production.
(
set -eu
psql --username "$POSTGRES_USER" --dbname postgres -v ON_ERROR_STOP=1 \
  --set runtime_password="$(cat /run/secrets/runtime_password)" \
  --set migrator_password="$(cat /run/secrets/migrator_password)" <<'SQL'
CREATE ROLE mma_stage_migrator LOGIN PASSWORD :'migrator_password' NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE ROLE mma_stage_runtime LOGIN PASSWORD :'runtime_password' NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE DATABASE mma_test_stage OWNER mma_stage_migrator;
CREATE DATABASE mma_test_restore OWNER mma_stage_migrator;
REVOKE ALL ON DATABASE mma_test_stage FROM PUBLIC;
REVOKE ALL ON DATABASE mma_test_restore FROM PUBLIC;
GRANT CONNECT ON DATABASE mma_test_stage, mma_test_restore TO mma_stage_migrator, mma_stage_runtime;
\connect mma_test_stage
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO mma_stage_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE mma_stage_migrator IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO mma_stage_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE mma_stage_migrator IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO mma_stage_runtime;
\connect mma_test_restore
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO mma_stage_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE mma_stage_migrator IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO mma_stage_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE mma_stage_migrator IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO mma_stage_runtime;
SQL
)
