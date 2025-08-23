from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_users"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # fallback system user
    system_user_id = "00000000-0000-0000-0000-000000000000"
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "INSERT INTO users (id, email, created_at) VALUES (:id, :email, now()) ON CONFLICT (id) DO NOTHING"
        ),
        {"id": system_user_id, "email": "system@localhost"},
    )

    op.add_column(
        "tasks",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text(f"'{system_user_id}'::uuid"),
        ),
    )

    op.create_index("ix_tasks_user_id", "tasks", ["user_id"])

    op.create_foreign_key(
        "fk_tasks_user_id_users",
        "tasks",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.alter_column("tasks", "user_id", server_default=None)


def downgrade() -> None:
    op.drop_constraint("fk_tasks_user_id_users", "tasks", type_="foreignkey")
    op.drop_index("ix_tasks_user_id", table_name="tasks")
    op.drop_column("tasks", "user_id")
    op.drop_table("users")
