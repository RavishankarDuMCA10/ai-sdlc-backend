"""Unit tests for the Alembic migration files.

These tests verify the SQL statements emitted by each migration's upgrade()
and downgrade() functions without requiring a live database connection.
"""
import importlib.util
import os
from types import ModuleType
from unittest.mock import MagicMock, patch


_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "migrations", "versions")


def _load_migration(filename: str) -> ModuleType:
    """Load a migration module from its file path (handles digit-prefixed names)."""
    file_path = os.path.join(_BASE_DIR, filename)
    spec = importlib.util.spec_from_file_location("_migration_module", file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestCarsMigration:
    """Tests for migration 0001 – cars table."""

    FILENAME = "0001_create_cars_table.py"

    def test_revision_metadata(self):
        mod = _load_migration(self.FILENAME)
        assert mod.revision == "0001"
        assert mod.down_revision is None

    def test_upgrade_creates_table(self):
        mod = _load_migration(self.FILENAME)
        mock_op = MagicMock()
        with patch.object(mod, "op", mock_op):
            mod.upgrade()

        executed_sql = " ".join(
            str(c.args[0]) for c in mock_op.execute.call_args_list
        ).lower()

        assert "create table" in executed_sql
        assert "cars" in executed_sql

    def test_upgrade_includes_required_columns(self):
        mod = _load_migration(self.FILENAME)
        mock_op = MagicMock()
        with patch.object(mod, "op", mock_op):
            mod.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0].args[0].lower()

        required_columns = [
            "id",
            "licence_plate",
            "make",
            "model",
            "year",
            "colour",
            "fuel_type",
            "seating_capacity",
            "current_location",
            "condition_rating",
            "status",
            "is_active",
            "next_service_date",
            "created_at",
            "updated_at",
        ]
        for col in required_columns:
            assert col in create_table_sql, f"Column '{col}' not found in CREATE TABLE statement"

    def test_upgrade_includes_constraints(self):
        mod = _load_migration(self.FILENAME)
        mock_op = MagicMock()
        with patch.object(mod, "op", mock_op):
            mod.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0].args[0].lower()

        assert "primary key" in create_table_sql
        assert "unique" in create_table_sql
        assert "petrol" in create_table_sql
        assert "diesel" in create_table_sql
        assert "electric" in create_table_sql
        assert "hybrid" in create_table_sql
        assert "available" in create_table_sql
        assert "reserved" in create_table_sql
        assert "rented" in create_table_sql
        assert "in_service" in create_table_sql
        assert "unavailable" in create_table_sql
        assert "inactive" in create_table_sql

    def test_upgrade_creates_indexes(self):
        mod = _load_migration(self.FILENAME)
        mock_op = MagicMock()
        with patch.object(mod, "op", mock_op):
            mod.upgrade()

        # First call is CREATE TABLE; remaining calls are CREATE INDEX
        index_calls = mock_op.execute.call_args_list[1:]
        assert len(index_calls) == 3

        index_sql = " ".join(str(c.args[0]) for c in index_calls).lower()
        assert "idx_cars_status" in index_sql
        assert "idx_cars_is_active" in index_sql
        assert "idx_cars_next_service_date" in index_sql

    def test_downgrade_drops_table(self):
        mod = _load_migration(self.FILENAME)
        mock_op = MagicMock()
        with patch.object(mod, "op", mock_op):
            mod.downgrade()

        executed_sql = mock_op.execute.call_args_list[0].args[0].lower()
        assert "drop table" in executed_sql
        assert "cars" in executed_sql


class TestCarServiceSchedulesMigration:
    """Tests for migration 0002 – car_service_schedules table."""

    FILENAME = "0002_create_car_service_schedules_table.py"

    def test_revision_metadata(self):
        mod = _load_migration(self.FILENAME)
        assert mod.revision == "0002"
        assert mod.down_revision == "0001"

    def test_upgrade_creates_table(self):
        mod = _load_migration(self.FILENAME)
        mock_op = MagicMock()
        with patch.object(mod, "op", mock_op):
            mod.upgrade()

        executed_sql = " ".join(
            str(c.args[0]) for c in mock_op.execute.call_args_list
        ).lower()

        assert "create table" in executed_sql
        assert "car_service_schedules" in executed_sql

    def test_upgrade_includes_required_columns(self):
        mod = _load_migration(self.FILENAME)
        mock_op = MagicMock()
        with patch.object(mod, "op", mock_op):
            mod.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0].args[0].lower()

        required_columns = [
            "id",
            "car_id",
            "service_type",
            "scheduled_date",
            "estimated_downtime_hours",
            "service_provider",
            "status",
            "notes",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        for col in required_columns:
            assert col in create_table_sql, f"Column '{col}' not found in CREATE TABLE statement"

    def test_upgrade_includes_foreign_key(self):
        mod = _load_migration(self.FILENAME)
        mock_op = MagicMock()
        with patch.object(mod, "op", mock_op):
            mod.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0].args[0].lower()
        assert "foreign key" in create_table_sql
        assert "references cars" in create_table_sql

    def test_upgrade_includes_status_constraint(self):
        mod = _load_migration(self.FILENAME)
        mock_op = MagicMock()
        with patch.object(mod, "op", mock_op):
            mod.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0].args[0].lower()
        assert "scheduled" in create_table_sql
        assert "in_progress" in create_table_sql
        assert "completed" in create_table_sql
        assert "cancelled" in create_table_sql

    def test_upgrade_creates_indexes(self):
        mod = _load_migration(self.FILENAME)
        mock_op = MagicMock()
        with patch.object(mod, "op", mock_op):
            mod.upgrade()

        index_calls = mock_op.execute.call_args_list[1:]
        assert len(index_calls) == 3

        index_sql = " ".join(str(c.args[0]) for c in index_calls).lower()
        assert "idx_car_service_schedules_car_id" in index_sql
        assert "idx_car_service_schedules_scheduled_date" in index_sql
        assert "idx_car_service_schedules_status" in index_sql

    def test_downgrade_drops_table(self):
        mod = _load_migration(self.FILENAME)
        mock_op = MagicMock()
        with patch.object(mod, "op", mock_op):
            mod.downgrade()

        executed_sql = mock_op.execute.call_args_list[0].args[0].lower()
        assert "drop table" in executed_sql
        assert "car_service_schedules" in executed_sql
