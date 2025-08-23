from __future__ import annotations
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from app.config import settings

config = context.config

database_url = settings.DATABASE_URL or config.get_main_option("sqlalchemy.url")
if not database_url:
    raise RuntimeError("DATABASE_URL must be set in env or in alembic.ini")
config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name:
    fileConfig(config.config_file_name)

from app.db.base import Base  # noqa
import app.models  # noqa

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
