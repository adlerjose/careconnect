"""Add triage records and message processing errors.

Revision ID: 0002_add_triage_records
Revises: 0001_patients_messages
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_add_triage_records"
down_revision = "0001_patients_messages"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("messages", sa.Column("processing_error", sa.Text(), nullable=True))
    op.create_table(
        "triage_records",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "patient_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("patients.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "message_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("clinical_summary", sa.Text(), nullable=True),
        sa.Column(
            "extracted_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "requires_human_review",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("message_id", name="uq_triage_records_message_id"),
    )
    op.create_index(
        "ix_triage_records_patient_id", "triage_records", ["patient_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_triage_records_patient_id", table_name="triage_records")
    op.drop_table("triage_records")
    op.drop_column("messages", "processing_error")
