"""create cars table

Revision ID: 0001
Revises:
Create Date: 2026-03-15
"""

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE cars (
            id                  UUID            NOT NULL,
            licence_plate       VARCHAR(20)     NOT NULL,
            make                VARCHAR(100)    NOT NULL,
            model               VARCHAR(100)    NOT NULL,
            year                SMALLINT        NOT NULL,
            colour              VARCHAR(50)     NOT NULL,
            fuel_type           VARCHAR(20)     NOT NULL,
            seating_capacity    SMALLINT        NOT NULL,
            current_location    VARCHAR(255)    NOT NULL,
            condition_rating    SMALLINT        NOT NULL,
            status              VARCHAR(30)     NOT NULL,
            is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
            next_service_date   DATE,
            created_at          TIMESTAMP       NOT NULL,
            updated_at          TIMESTAMP       NOT NULL,
            CONSTRAINT cars_pkey PRIMARY KEY (id),
            CONSTRAINT cars_licence_plate_key UNIQUE (licence_plate),
            CONSTRAINT cars_fuel_type_check CHECK (
                fuel_type IN ('petrol', 'diesel', 'electric', 'hybrid')
            ),
            CONSTRAINT cars_status_check CHECK (
                status IN ('available', 'reserved', 'rented', 'in_service', 'unavailable', 'inactive')
            ),
            CONSTRAINT cars_condition_rating_check CHECK (
                condition_rating BETWEEN 1 AND 10
            ),
            CONSTRAINT cars_year_check CHECK (year > 0)
        )
        """
    )

    op.execute(
        "CREATE INDEX idx_cars_status ON cars (status)"
    )
    op.execute(
        "CREATE INDEX idx_cars_is_active ON cars (is_active)"
    )
    op.execute(
        "CREATE INDEX idx_cars_licence_plate ON cars (licence_plate)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_cars_licence_plate")
    op.execute("DROP INDEX IF EXISTS idx_cars_is_active")
    op.execute("DROP INDEX IF EXISTS idx_cars_status")
    op.execute("DROP TABLE IF EXISTS cars")
