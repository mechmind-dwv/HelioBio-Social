from logging.config import fileConfig
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(backend_path))

from sqlalchemy import engine_from_config, pool
from alembic import context
import importlib.util
import os
os.environ['ALEMBIC_IGNORE_MISSING_REVISIONS'] = '1'

# Carga database.py
database_path = backend_path / "database.py"
spec = importlib.util.spec_from_file_location("database_module", database_path)
database_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database_module)
Base = database_module.Base

# Carga modelos
models_path = backend_path / "database" / "models" / "mental_health_data.py"
spec = importlib.util.spec_from_file_location("models_module", models_path)
models_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models_module)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
