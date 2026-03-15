"""create cars table

Revision ID: 0001
Revises:
Create Date: 2026-03-15

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS cars (
            id               UUID         NOT NULL DEFAULT gen_random_uuid(),
            licence_plate    VARCHAR(20)  NOT NULL,
            make             VARCHAR(100) NOT NULL,
            model            VARCHAR(100) NOT NULL,
            year             SMALLINT     NOT NULL,
            colour           VARCHAR(50)  NOT NULL,
            fuel_type        VARCHAR(20)  NOT NULL,
            seating_capacity SMALLINT     NOT NULL,
            current_location VARCHAR(255) NOT NULL,
            condition_rating SMALLINT     NOT NULL,
            status           VARCHAR(30)  NOT NULL,
            is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
            next_service_date DATE,
            created_at       TIMESTAMP    NOT NULL DEFAULT NOW(),
            updated_at       TIMESTAMP    NOT NULL DEFAULT NOW(),
            CONSTRAINT cars_pkey PRIMARY KEY (id),
            CONSTRAINT cars_licence_plate_unique UNIQUE (licence_plate),
            CONSTRAINT cars_fuel_type_check CHECK (
                fuel_type IN ('petrol', 'diesel', 'electric', 'hybrid')
            ),
            CONSTRAINT cars_status_check CHECK (
                status IN ('available', 'reserved', 'rented', 'in_service', 'unavailable', 'inactive')
            ),
            CONSTRAINT cars_condition_rating_check CHECK (
                condition_rating BETWEEN 1 AND 10
            )
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_cars_status ON cars (status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_cars_is_active ON cars (is_active)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_cars_next_service_date ON cars (next_service_date)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS cars")
