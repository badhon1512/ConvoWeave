"""Create conversation records.

Revision ID: 0001
Revises:
Create Date: 2026-09-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "transcripts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("language_code", sa.String(length=10), nullable=True),
        sa.Column("language_probability", sa.Float(), nullable=True),
        sa.Column("full_text", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model_id", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["conversations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_transcripts_conversation_id"),
        "transcripts",
        ["conversation_id"],
    )
    op.create_table(
        "speakers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("transcript_id", sa.Uuid(), nullable=False),
        sa.Column("provider_speaker_id", sa.String(length=100), nullable=False),
        sa.Column("display_name", sa.String(length=80), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["transcript_id"], ["transcripts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "transcript_id", "provider_speaker_id", name="uq_transcript_speaker"
        ),
    )
    op.create_index(
        op.f("ix_speakers_transcript_id"), "speakers", ["transcript_id"]
    )
    op.create_table(
        "turns",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("transcript_id", sa.Uuid(), nullable=False),
        sa.Column("speaker_id", sa.Uuid(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("start", sa.Float(), nullable=False),
        sa.Column("end", sa.Float(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("words", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["speaker_id"], ["speakers.id"]),
        sa.ForeignKeyConstraint(
            ["transcript_id"], ["transcripts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transcript_id", "sequence", name="uq_transcript_turn"),
    )
    op.create_index(op.f("ix_turns_transcript_id"), "turns", ["transcript_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_turns_transcript_id"), table_name="turns")
    op.drop_table("turns")
    op.drop_index(op.f("ix_speakers_transcript_id"), table_name="speakers")
    op.drop_table("speakers")
    op.drop_index(op.f("ix_transcripts_conversation_id"), table_name="transcripts")
    op.drop_table("transcripts")
    op.drop_table("conversations")

