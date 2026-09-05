-- ============================================================
--  PAY_CORE  —  Stage 2 Schema
--  Tables:  transactions  |  ledger_entries
--  Run this AFTER stage_1_schema.sql
-- ============================================================


-- ─── Transactions ────────────────────────────────────────────────────────────
-- Master record of every money movement in the system.
-- One transaction = one business event (a transfer, a payment, etc.)
--
-- `reference` is a unique human-readable ID returned to the user.
-- `status` lifecycle:  pending → completed | failed
-- `type`   lifecycle:  Stage 2 = 'transfer'  |  Stage 3+ = 'payment_request'

CREATE TABLE IF NOT EXISTS transactions (
    id                 SERIAL        PRIMARY KEY,
    reference          VARCHAR(50)   NOT NULL UNIQUE,
    sender_wallet_id   INTEGER       NOT NULL REFERENCES wallets(id),
    receiver_wallet_id INTEGER       NOT NULL REFERENCES wallets(id),
    amount             BIGINT        NOT NULL CHECK (amount > 0),
    currency           VARCHAR(10)   NOT NULL DEFAULT 'PKR',
    type               VARCHAR(30)   NOT NULL DEFAULT 'transfer',
    status             VARCHAR(20)   NOT NULL DEFAULT 'pending',
    created_at         TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);


-- ─── Ledger Entries ───────────────────────────────────────────────────────────
-- Double-entry bookkeeping: every transaction produces exactly TWO rows.
--
--   Transfer 500  A → B
--   ─────────────────────────────────────────────────
--   transaction_id | wallet_id | entry_type | amount
--        1         |  A wallet |   DEBIT    |  500
--        1         |  B wallet |   CREDIT   |  500
--
-- Rule: SUM(DEBIT) must always equal SUM(CREDIT) per transaction.
-- This lets you audit the full money trail for any wallet at any time.

CREATE TABLE IF NOT EXISTS ledger_entries (
    id             SERIAL       PRIMARY KEY,
    transaction_id INTEGER      NOT NULL REFERENCES transactions(id),
    wallet_id      INTEGER      NOT NULL REFERENCES wallets(id),
    entry_type     VARCHAR(10)  NOT NULL CHECK (entry_type IN ('debit', 'credit')),
    amount         BIGINT       NOT NULL CHECK (amount > 0),
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);


-- ─── Indexes ─────────────────────────────────────────────────────────────────
-- Speed up the common queries: "show me this wallet's transaction history"

CREATE INDEX IF NOT EXISTS idx_transactions_sender
    ON transactions(sender_wallet_id);

CREATE INDEX IF NOT EXISTS idx_transactions_receiver
    ON transactions(receiver_wallet_id);

CREATE INDEX IF NOT EXISTS idx_ledger_wallet
    ON ledger_entries(wallet_id);

CREATE INDEX IF NOT EXISTS idx_transactions_reference
    ON transactions(reference);
