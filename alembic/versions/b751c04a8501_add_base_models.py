"""add base models

Revision ID: b751c04a8501
Revises:
Create Date: 2026-05-07 23:29:51.308924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b751c04a8501'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:

    admin_user_role_enum = sa.Enum(
        'super_admin', 'museum_admin', 'museum_stuff',
        name='userroleenum',
    )
    op.create_table(
        'admin_user',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('role', admin_user_role_enum, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('museum_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.Column('updated_by', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )

    museum_status_enum = sa.Enum(
        'active', 'trial', 'inactive', 'blocked',
        name='museumstatusenum',
    )
    subscription_plan_enum = sa.Enum(
        'free', 'basic', 'premium',
        name='subscriptionplanenum',
    )
    op.create_table(
        'museum',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('legal_name', sa.String(length=255), nullable=False),
        sa.Column('inn', sa.String(length=12), nullable=False),
        sa.Column('ogrn', sa.String(length=13), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=11), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=False),
        sa.Column('status', museum_status_enum, nullable=False),
        sa.Column('subscription_plan', subscription_plan_enum, nullable=False),
        sa.Column('subscription_end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.Column('updated_by', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['admin_user.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['admin_user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('inn'),
        sa.UniqueConstraint('ogrn'),
    )

    op.create_foreign_key(
        'admin_user_museum_id_fkey', 'admin_user', 'museum', ['museum_id'], ['id']
    )
    op.create_foreign_key(
        'admin_user_created_by_fkey', 'admin_user', 'admin_user', ['created_by'], ['id']
    )
    op.create_foreign_key(
        'admin_user_updated_by_fkey', 'admin_user', 'admin_user', ['updated_by'], ['id']
    )

    op.create_table(
        'admin_user_audit',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('action', sa.String(length=255), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['admin_user.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'event_location',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('museum_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.Column('updated_by', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['museum_id'], ['museum.id']),
        sa.ForeignKeyConstraint(['created_by'], ['admin_user.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['admin_user.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'event_type',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.Column('updated_by', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['admin_user.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['admin_user.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    event_status_enum = sa.Enum(
        'draft', 'published', 'archived', 'canceled',
        name='eventstatusenum',
    )
    op.create_table(
        'event',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('date_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('date_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', event_status_enum, nullable=False),
        sa.Column('is_recurring', sa.Boolean(), nullable=False),
        sa.Column('museum_id', sa.BigInteger(), nullable=False),
        sa.Column('type_id', sa.BigInteger(), nullable=False),
        sa.Column('location_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.Column('updated_by', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['admin_user.id']),
        sa.ForeignKeyConstraint(['location_id'], ['event_location.id']),
        sa.ForeignKeyConstraint(['museum_id'], ['museum.id']),
        sa.ForeignKeyConstraint(['type_id'], ['event_type.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['admin_user.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('event')
    op.drop_table('event_type')
    op.drop_table('event_location')
    op.drop_table('admin_user_audit')
    op.drop_constraint('admin_user_updated_by_fkey', 'admin_user', type_='foreignkey')
    op.drop_constraint('admin_user_created_by_fkey', 'admin_user', type_='foreignkey')
    op.drop_constraint('admin_user_museum_id_fkey', 'admin_user', type_='foreignkey')
    op.drop_table('museum')
    op.drop_table('admin_user')

    op.execute('DROP TYPE IF EXISTS userroleenum')
    op.execute('DROP TYPE IF EXISTS museumstatusenum')
    op.execute('DROP TYPE IF EXISTS subscriptionplanenum')
    op.execute('DROP TYPE IF EXISTS eventstatusenum')
