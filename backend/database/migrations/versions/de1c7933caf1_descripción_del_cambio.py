"""Descripción del cambio

Revision ID: de1c7933caf1
Revises: 46f2bc725c24
Create Date: 2026-01-16 00:43:40.072355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de1c7933caf1'
down_revision: Union[str, None] = '46f2bc725c24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
