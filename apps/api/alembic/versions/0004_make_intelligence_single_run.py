"""Make conversation intelligence single-run.

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            DELETE FROM intelligence_artifacts
            WHERE id IN (
                SELECT id
                FROM (
                    SELECT id, ROW_NUMBER() OVER (
                        PARTITION BY conversation_id, kind
                        ORDER BY version, created_at
                    ) AS position
                    FROM intelligence_artifacts
                ) duplicates
                WHERE position > 1
            )
            """
        )
    )
    op.drop_constraint(
        "uq_intelligence_version",
        "intelligence_artifacts",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_intelligence_conversation_kind",
        "intelligence_artifacts",
        ["conversation_id", "kind"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_intelligence_conversation_kind",
        "intelligence_artifacts",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_intelligence_version",
        "intelligence_artifacts",
        ["conversation_id", "kind", "version"],
    )
