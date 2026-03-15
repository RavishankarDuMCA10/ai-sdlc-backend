"""create car_service_schedules table

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-15 10:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'car_service_schedules',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('car_id', UUID(as_uuid=True), nullable=False),
        sa.Column('service_type', sa.String(100), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('estimated_downtime_hours', sa.Numeric(5, 2), nullable=True),
        sa.Column('service_provider', sa.String(255), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['car_id'], ['cars.id'], name='fk_car_service_schedules_car_id', ondelete='CASCADE'),
    )

    # Check constraint on status
    op.create_check_constraint(
        'ck_car_service_schedules_status',
        'car_service_schedules',
        "status IN ('scheduled', 'in_progress', 'completed', 'cancelled')"
    )

    # Indexes
    op.create_index('ix_car_service_schedules_car_id', 'car_service_schedules', ['car_id'])
    op.create_index('ix_car_service_schedules_status', 'car_service_schedules', ['status'])
    op.create_index('ix_car_service_schedules_scheduled_date', 'car_service_schedules', ['scheduled_date'])


def downgrade() -> None:
    op.drop_index('ix_car_service_schedules_scheduled_date', table_name='car_service_schedules')
    op.drop_index('ix_car_service_schedules_status', table_name='car_service_schedules')
    op.drop_index('ix_car_service_schedules_car_id', table_name='car_service_schedules')
    op.drop_table('car_service_schedules')
