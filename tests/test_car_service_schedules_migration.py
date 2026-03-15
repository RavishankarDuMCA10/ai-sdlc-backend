"""Unit tests for the car_service_schedules table migration (0002)."""

import importlib.util
import os
from unittest.mock import MagicMock, patch

import pytest

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "..", "migrations", "versions")


def load_migration(filename):
    filepath = os.path.join(MIGRATIONS_DIR, filename)
    spec = importlib.util.spec_from_file_location("migration", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def schedules_migration():
    return load_migration("0002_create_car_service_schedules_table.py")


class TestCarServiceSchedulesMigrationMetadata:
    def test_revision_id(self, schedules_migration):
        assert schedules_migration.revision == "0002"

    def test_down_revision(self, schedules_migration):
        assert schedules_migration.down_revision == "0001"

    def test_branch_labels_is_none(self, schedules_migration):
        assert schedules_migration.branch_labels is None

    def test_depends_on_is_none(self, schedules_migration):
        assert schedules_migration.depends_on is None


class TestCarServiceSchedulesUpgrade:
    def test_upgrade_creates_table(self, schedules_migration):
        mock_op = MagicMock()
        with patch.object(schedules_migration, "op", mock_op):
            schedules_migration.upgrade()

        execute_calls = mock_op.execute.call_args_list
        assert len(execute_calls) == 4

        create_table_sql = execute_calls[0][0][0]
        assert "CREATE TABLE car_service_schedules" in create_table_sql

    def test_upgrade_includes_all_columns(self, schedules_migration):
        mock_op = MagicMock()
        with patch.object(schedules_migration, "op", mock_op):
            schedules_migration.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0][0][0]
        expected_columns = [
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
        for col in expected_columns:
            assert col in create_table_sql, f"Column '{col}' not found in CREATE TABLE SQL"

    def test_upgrade_includes_primary_key_constraint(self, schedules_migration):
        mock_op = MagicMock()
        with patch.object(schedules_migration, "op", mock_op):
            schedules_migration.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0][0][0]
        assert "PRIMARY KEY" in create_table_sql
        assert "car_service_schedules_pkey" in create_table_sql

    def test_upgrade_includes_foreign_key_to_cars(self, schedules_migration):
        mock_op = MagicMock()
        with patch.object(schedules_migration, "op", mock_op):
            schedules_migration.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0][0][0]
        assert "car_service_schedules_car_id_fkey" in create_table_sql
        assert "FOREIGN KEY (car_id) REFERENCES cars (id)" in create_table_sql

    def test_upgrade_includes_status_check_constraint(self, schedules_migration):
        mock_op = MagicMock()
        with patch.object(schedules_migration, "op", mock_op):
            schedules_migration.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0][0][0]
        assert "car_service_schedules_status_check" in create_table_sql
        for status in ("scheduled", "in_progress", "completed", "cancelled"):
            assert status in create_table_sql

    def test_upgrade_nullable_optional_columns(self, schedules_migration):
        mock_op = MagicMock()
        with patch.object(schedules_migration, "op", mock_op):
            schedules_migration.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0][0][0]
        lines = create_table_sql.splitlines()
        nullable_cols = ["estimated_downtime_hours", "service_provider", "notes", "completed_at"]
        for col in nullable_cols:
            col_line = next((line for line in lines if col in line), None)
            assert col_line is not None, f"Column '{col}' not found"
            assert "NOT NULL" not in col_line, f"Column '{col}' should be nullable"

    def test_upgrade_creates_car_id_index(self, schedules_migration):
        mock_op = MagicMock()
        with patch.object(schedules_migration, "op", mock_op):
            schedules_migration.upgrade()

        index_calls = [str(c) for c in mock_op.execute.call_args_list[1:]]
        assert any("idx_car_service_schedules_car_id" in c for c in index_calls)

    def test_upgrade_creates_status_index(self, schedules_migration):
        mock_op = MagicMock()
        with patch.object(schedules_migration, "op", mock_op):
            schedules_migration.upgrade()

        index_calls = [str(c) for c in mock_op.execute.call_args_list[1:]]
        assert any("idx_car_service_schedules_status" in c for c in index_calls)

    def test_upgrade_creates_scheduled_date_index(self, schedules_migration):
        mock_op = MagicMock()
        with patch.object(schedules_migration, "op", mock_op):
            schedules_migration.upgrade()

        index_calls = [str(c) for c in mock_op.execute.call_args_list[1:]]
        assert any("idx_car_service_schedules_scheduled_date" in c for c in index_calls)

    def test_upgrade_estimated_downtime_hours_is_decimal(self, schedules_migration):
        mock_op = MagicMock()
        with patch.object(schedules_migration, "op", mock_op):
            schedules_migration.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0][0][0]
        assert "DECIMAL(5, 2)" in create_table_sql


class TestCarServiceSchedulesDowngrade:
    def test_downgrade_drops_indexes_before_table(self, schedules_migration):
        mock_op = MagicMock()
        with patch.object(schedules_migration, "op", mock_op):
            schedules_migration.downgrade()

        calls = [c[0][0] for c in mock_op.execute.call_args_list]
        table_drop_index = next(i for i, sql in enumerate(calls) if "DROP TABLE" in sql)
        for i, sql in enumerate(calls):
            if "DROP INDEX" in sql:
                assert i < table_drop_index

    def test_downgrade_drops_all_indexes(self, schedules_migration):
        mock_op = MagicMock()
        with patch.object(schedules_migration, "op", mock_op):
            schedules_migration.downgrade()

        sqls = [c[0][0] for c in mock_op.execute.call_args_list]
        expected_indexes = [
            "idx_car_service_schedules_scheduled_date",
            "idx_car_service_schedules_status",
            "idx_car_service_schedules_car_id",
        ]
        for idx in expected_indexes:
            assert any(idx in sql for sql in sqls), f"Index '{idx}' not dropped in downgrade"

    def test_downgrade_drops_car_service_schedules_table(self, schedules_migration):
        mock_op = MagicMock()
        with patch.object(schedules_migration, "op", mock_op):
            schedules_migration.downgrade()

        sqls = [c[0][0] for c in mock_op.execute.call_args_list]
        assert any("DROP TABLE IF EXISTS car_service_schedules" in sql for sql in sqls)
