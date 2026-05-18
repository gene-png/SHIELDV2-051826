"""baseline schema for SHIELD v2.0

Revision ID: 0001_baseline
Revises:
Create Date: 2026-05-18

Creates all ~22 application tables from `Base.metadata` and installs the
non-table objects the spec mandates:

* `audit_entries` append-only trigger (rejects UPDATE/DELETE)
* `artifacts.origin` immutability trigger (rejects UPDATE once set)
* generic `set_updated_at` trigger applied to every table with `updated_at`
* partial-unique index ensuring at most one row in `client` (singleton)
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

from app.models import Base  # noqa: F401 (imports all model modules)

revision: str = "0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Master Spec §11 — append-only audit log enforced at DB layer.
AUDIT_TRIGGER_SQL = """
CREATE OR REPLACE FUNCTION audit_entries_no_modify() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'audit_entries is append-only (Master Spec §11)';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS audit_entries_no_update ON audit_entries;
CREATE TRIGGER audit_entries_no_update
    BEFORE UPDATE ON audit_entries
    FOR EACH ROW EXECUTE FUNCTION audit_entries_no_modify();

DROP TRIGGER IF EXISTS audit_entries_no_delete ON audit_entries;
CREATE TRIGGER audit_entries_no_delete
    BEFORE DELETE ON audit_entries
    FOR EACH ROW EXECUTE FUNCTION audit_entries_no_modify();
"""

# Master Spec §11 — artifact origin is immutable once set.
ORIGIN_IMMUTABILITY_SQL = """
CREATE OR REPLACE FUNCTION artifacts_origin_immutable() RETURNS trigger AS $$
BEGIN
    IF OLD.origin IS NOT NULL AND NEW.origin IS DISTINCT FROM OLD.origin THEN
        RAISE EXCEPTION 'artifacts.origin is immutable once set (Master Spec §11)';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS artifacts_origin_immutable ON artifacts;
CREATE TRIGGER artifacts_origin_immutable
    BEFORE UPDATE OF origin ON artifacts
    FOR EACH ROW EXECUTE FUNCTION artifacts_origin_immutable();
"""

# Generic updated_at trigger — applied to every table that has the column.
UPDATED_AT_FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

UPDATED_AT_APPLY_SQL = """
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN
        SELECT table_name
        FROM information_schema.columns
        WHERE column_name = 'updated_at'
          AND table_schema = 'public'
    LOOP
        EXECUTE format(
            'DROP TRIGGER IF EXISTS set_updated_at ON %I; '
            'CREATE TRIGGER set_updated_at BEFORE UPDATE ON %I '
            'FOR EACH ROW EXECUTE FUNCTION set_updated_at();',
            t, t
        );
    END LOOP;
END $$;
"""

CLIENT_SINGLETON_SQL = """
CREATE UNIQUE INDEX IF NOT EXISTS uq_client_singleton ON client ((true));
"""


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

    op.execute(AUDIT_TRIGGER_SQL)
    op.execute(ORIGIN_IMMUTABILITY_SQL)
    op.execute(UPDATED_AT_FUNCTION_SQL)
    op.execute(UPDATED_AT_APPLY_SQL)
    op.execute(CLIENT_SINGLETON_SQL)


def downgrade() -> None:
    bind = op.get_bind()
    op.execute("DROP INDEX IF EXISTS uq_client_singleton")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at CASCADE")
    op.execute("DROP FUNCTION IF EXISTS artifacts_origin_immutable CASCADE")
    op.execute("DROP FUNCTION IF EXISTS audit_entries_no_modify CASCADE")
    Base.metadata.drop_all(bind=bind)
