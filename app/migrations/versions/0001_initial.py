from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def get_taskstatus_enum(create_type: bool = True):
    return postgresql.ENUM(
        "created", "in_progress", "done", name="task_status", create_type=create_type
    )


def upgrade():
    task_status = get_taskstatus_enum()
    task_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            get_taskstatus_enum(False),
            nullable=False,
            server_default=sa.text("'created'::task_status"),
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )


def downgrade():
    op.drop_table("tasks")
    get_taskstatus_enum(False).drop(op.get_bind(), checkfirst=True)
