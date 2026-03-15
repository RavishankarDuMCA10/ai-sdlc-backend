"""create car_service_schedules table

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-15
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE car_service_schedules (
            id                          UUID            NOT NULL,
            car_id                      UUID            NOT NULL,
            service_type                VARCHAR(100)    NOT NULL,
            scheduled_date              DATE            NOT NULL,
            estimated_downtime_hours    DECIMAL(5, 2),
            service_provider            VARCHAR(255),
            status                      VARCHAR(20)     NOT NULL,
            notes                       TEXT,
            completed_at                TIMESTAMP,
            created_at                  TIMESTAMP       NOT NULL,
            updated_at                  TIMESTAMP       NOT NULL,
            CONSTRAINT car_service_schedules_pkey PRIMARY KEY (id),
            CONSTRAINT car_service_schedules_car_id_fkey
                FOREIGN KEY (car_id) REFERENCES cars (id),
            CONSTRAINT car_service_schedules_status_check CHECK (
                status IN ('scheduled', 'in_progress', 'completed', 'cancelled')
            )
        )
        """
    )

    op.execute(
        "CREATE INDEX idx_car_service_schedules_car_id ON car_service_schedules (car_id)"
    )
    op.execute(
        "CREATE INDEX idx_car_service_schedules_status ON car_service_schedules (status)"
    )
    op.execute(
        "CREATE INDEX idx_car_service_schedules_scheduled_date ON car_service_schedules (scheduled_date)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_car_service_schedules_scheduled_date")
    op.execute("DROP INDEX IF EXISTS idx_car_service_schedules_status")
    op.execute("DROP INDEX IF EXISTS idx_car_service_schedules_car_id")
    op.execute("DROP TABLE IF EXISTS car_service_schedules")
