"""Initial schema: create users and films tables

Revision ID: 3a8f56e2c34c
Revises:
Create Date: 2025-08-24 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3a8f56e2c34c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_users_email', 'email')
    )

    op.create_table(
        'films',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('genre', sa.String(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_films_title', 'title'),
        sa.Index('ix_films_genre', 'genre')
    )


def downgrade() -> None:
    op.drop_table('films')
    op.drop_table('users')
