-- ============================================================
--  PAY_CORE  —  Stage 3 Schema
--  Tables:  idempotency_keys  |  audit_logs
--  Run this AFTER stage_2_schema.sql
-- ============================================================


-- ─── Idempotency Keys ────────────────────────────────────────────────────────
-- Stores client-generated keys so the server can detect duplicate requests.
--
-- Workflow:
--   Client sends Idempotency-Key header with every transfer request.
--   Server checks this table before processing.
--   If key found  → return saved response (no double charge).
--   If key absent → process, save key + response, return response.
--
-- Keys expire after 24 hours — old keys are cleaned up by a background job
-- (added in Stage 5 with Celery). Until then, expired rows are ignored via
-- the WHERE expires_at > NOW() check in the repository.

CREATE TABLE IF NOT EXISTS idempotency_keys (
    id            SERIAL        PRIMARY KEY,
    key           VARCHAR(255)  NOT NULL,
    user_id       INTEGER       NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    endpoint      VARCHAR(100)  NOT NULL,
    response_body TEXT          NOT NULL,
    expires_at    TIMESTAMPTZ   NOT NULL,
    created_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    -- A key is unique per user + endpoint combination.
    -- This allows the same UUID to be reused across different endpoints
    -- by different users without collision.
    UNIQUE (key, user_id, endpoint)
);


-- ─── Audit Logs ───────────────────────────────────────────────────────────────
-- Permanent record of every security-relevant action in the system.
--
-- Unlike transactions (financial records), audit logs are security records.
-- They answer: WHO did WHAT to WHICH resource from WHERE and WHEN.
--
-- Audit logs are NEVER deleted — they are a compliance requirement.
-- Even if a user deletes their account, their audit history remains.

CREATE TABLE IF NOT EXISTS audit_logs (
    id          SERIAL        PRIMARY KEY,
    user_id     INTEGER       REFERENCES users(id) ON DELETE SET NULL,
    action      VARCHAR(100)  NOT NULL,
    resource    VARCHAR(100),
    resource_id VARCHAR(100),
    ip_address  VARCHAR(50),
    metadata    TEXT,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);


-- ─── Indexes ──────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_idempotency_key_lookup
    ON idempotency_keys(key, user_id, endpoint);

CREATE INDEX IF NOT EXISTS idx_audit_user
    ON audit_logs(user_id);

CREATE INDEX IF NOT EXISTS idx_audit_action
    ON audit_logs(action);

CREATE INDEX IF NOT EXISTS idx_audit_created
    ON audit_logs(created_at DESC);
