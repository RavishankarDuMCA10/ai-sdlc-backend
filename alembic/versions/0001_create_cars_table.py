"""create cars table

Revision ID: 0001
Revises: 
Create Date: 2026-03-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        'cars',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('licence_plate', sa.String(20), nullable=False),
        sa.Column('make', sa.String(100), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('year', sa.SmallInteger(), nullable=False),
        sa.Column('colour', sa.String(50), nullable=False),
        sa.Column('fuel_type', sa.String(20), nullable=False),
        sa.Column('seating_capacity', sa.SmallInteger(), nullable=False),
        sa.Column('current_location', sa.String(255), nullable=False),
        sa.Column('condition_rating', sa.SmallInteger(), nullable=False),
        sa.Column('status', sa.String(30), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('next_service_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
    )

    # Unique constraint
    op.create_unique_constraint('uq_cars_licence_plate', 'cars', ['licence_plate'])

    # Check constraints
    op.create_check_constraint(
        'ck_cars_fuel_type',
        'cars',
        "fuel_type IN ('petrol', 'diesel', 'electric', 'hybrid')"
    )
    op.create_check_constraint(
        'ck_cars_status',
        'cars',
        "status IN ('available', 'reserved', 'rented', 'in_service', 'unavailable', 'inactive')"
    )
    op.create_check_constraint(
        'ck_cars_condition_rating',
        'cars',
        'condition_rating BETWEEN 1 AND 10'
    )
    op.create_check_constraint(
        'ck_cars_year',
        'cars',
        'year > 1900'
    )
    op.create_check_constraint(
        'ck_cars_seating_capacity',
        'cars',
        'seating_capacity > 0'
    )

    # Indexes
    op.create_index('ix_cars_status', 'cars', ['status'])
    op.create_index('ix_cars_is_active', 'cars', ['is_active'])
    op.create_index('ix_cars_fuel_type', 'cars', ['fuel_type'])


def downgrade() -> None:
    op.drop_index('ix_cars_fuel_type', table_name='cars')
    op.drop_index('ix_cars_is_active', table_name='cars')
    op.drop_index('ix_cars_status', table_name='cars')
    op.drop_table('cars')
