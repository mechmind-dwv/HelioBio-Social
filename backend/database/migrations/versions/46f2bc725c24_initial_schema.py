"""Initial schema

Revision ID: 46f2bc725c24
Revises: 
Create Date: 2026-01-16 00:34:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '46f2bc725c24'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create mental_health_data table
    op.create_table(
        'mental_health_data',
        sa.Column('time', sa.DateTime(timezone=True), primary_key=True, nullable=False),
        sa.Column('region', sa.String(), nullable=False),
        sa.Column('psychiatric_admissions', sa.Integer(), nullable=True),
        sa.Column('suicide_rate', sa.Float(), nullable=True),
        sa.Column('bipolar_episodes', sa.Integer(), nullable=True),
        sa.Column('depression_index', sa.Float(), nullable=True),
    )
    
    # Create mental_health_summary table
    op.create_table(
        'mental_health_summary',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('global_depression_index', sa.Float(), nullable=True),
        sa.Column('global_suicide_rate', sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('mental_health_summary')
    op.drop_table('mental_health_data')
