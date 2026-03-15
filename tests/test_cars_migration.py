"""Unit tests for the cars table migration (0001_create_cars_table)."""

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
def cars_migration():
    return load_migration("0001_create_cars_table.py")


class TestCarsMigrationMetadata:
    def test_revision_id(self, cars_migration):
        assert cars_migration.revision == "0001"

    def test_down_revision_is_none(self, cars_migration):
        assert cars_migration.down_revision is None

    def test_branch_labels_is_none(self, cars_migration):
        assert cars_migration.branch_labels is None

    def test_depends_on_is_none(self, cars_migration):
        assert cars_migration.depends_on is None


class TestCarsUpgrade:
    def test_upgrade_creates_cars_table(self, cars_migration):
        mock_op = MagicMock()
        with patch.object(cars_migration, "op", mock_op):
            cars_migration.upgrade()

        execute_calls = mock_op.execute.call_args_list
        assert len(execute_calls) == 4

        create_table_sql = execute_calls[0][0][0]
        assert "CREATE TABLE cars" in create_table_sql

    def test_upgrade_includes_all_columns(self, cars_migration):
        mock_op = MagicMock()
        with patch.object(cars_migration, "op", mock_op):
            cars_migration.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0][0][0]
        expected_columns = [
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
        for col in expected_columns:
            assert col in create_table_sql, f"Column '{col}' not found in CREATE TABLE SQL"

    def test_upgrade_includes_primary_key_constraint(self, cars_migration):
        mock_op = MagicMock()
        with patch.object(cars_migration, "op", mock_op):
            cars_migration.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0][0][0]
        assert "PRIMARY KEY" in create_table_sql
        assert "cars_pkey" in create_table_sql

    def test_upgrade_includes_unique_constraint_on_licence_plate(self, cars_migration):
        mock_op = MagicMock()
        with patch.object(cars_migration, "op", mock_op):
            cars_migration.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0][0][0]
        assert "cars_licence_plate_key" in create_table_sql
        assert "UNIQUE" in create_table_sql

    def test_upgrade_includes_fuel_type_check_constraint(self, cars_migration):
        mock_op = MagicMock()
        with patch.object(cars_migration, "op", mock_op):
            cars_migration.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0][0][0]
        assert "cars_fuel_type_check" in create_table_sql
        for fuel in ("petrol", "diesel", "electric", "hybrid"):
            assert fuel in create_table_sql

    def test_upgrade_includes_status_check_constraint(self, cars_migration):
        mock_op = MagicMock()
        with patch.object(cars_migration, "op", mock_op):
            cars_migration.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0][0][0]
        assert "cars_status_check" in create_table_sql
        for status in ("available", "reserved", "rented", "in_service", "unavailable", "inactive"):
            assert status in create_table_sql

    def test_upgrade_includes_condition_rating_check_constraint(self, cars_migration):
        mock_op = MagicMock()
        with patch.object(cars_migration, "op", mock_op):
            cars_migration.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0][0][0]
        assert "cars_condition_rating_check" in create_table_sql
        assert "BETWEEN 1 AND 10" in create_table_sql

    def test_upgrade_creates_status_index(self, cars_migration):
        mock_op = MagicMock()
        with patch.object(cars_migration, "op", mock_op):
            cars_migration.upgrade()

        index_calls = [str(c) for c in mock_op.execute.call_args_list[1:]]
        assert any("idx_cars_status" in c for c in index_calls)

    def test_upgrade_creates_is_active_index(self, cars_migration):
        mock_op = MagicMock()
        with patch.object(cars_migration, "op", mock_op):
            cars_migration.upgrade()

        index_calls = [str(c) for c in mock_op.execute.call_args_list[1:]]
        assert any("idx_cars_is_active" in c for c in index_calls)

    def test_upgrade_creates_licence_plate_index(self, cars_migration):
        mock_op = MagicMock()
        with patch.object(cars_migration, "op", mock_op):
            cars_migration.upgrade()

        index_calls = [str(c) for c in mock_op.execute.call_args_list[1:]]
        assert any("idx_cars_licence_plate" in c for c in index_calls)

    def test_upgrade_includes_is_active_default_true(self, cars_migration):
        mock_op = MagicMock()
        with patch.object(cars_migration, "op", mock_op):
            cars_migration.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0][0][0]
        assert "DEFAULT TRUE" in create_table_sql

    def test_upgrade_next_service_date_is_nullable(self, cars_migration):
        mock_op = MagicMock()
        with patch.object(cars_migration, "op", mock_op):
            cars_migration.upgrade()

        create_table_sql = mock_op.execute.call_args_list[0][0][0]
        assert "next_service_date" in create_table_sql
        lines = create_table_sql.splitlines()
        date_line = next(line for line in lines if "next_service_date" in line)
        assert "NOT NULL" not in date_line


class TestCarsDowngrade:
    def test_downgrade_drops_indexes_before_table(self, cars_migration):
        mock_op = MagicMock()
        with patch.object(cars_migration, "op", mock_op):
            cars_migration.downgrade()

        calls = [c[0][0] for c in mock_op.execute.call_args_list]
        table_drop_index = next(i for i, sql in enumerate(calls) if "DROP TABLE" in sql)
        for i, sql in enumerate(calls):
            if "DROP INDEX" in sql:
                assert i < table_drop_index

    def test_downgrade_drops_all_indexes(self, cars_migration):
        mock_op = MagicMock()
        with patch.object(cars_migration, "op", mock_op):
            cars_migration.downgrade()

        sqls = [c[0][0] for c in mock_op.execute.call_args_list]
        expected_indexes = [
            "idx_cars_licence_plate",
            "idx_cars_is_active",
            "idx_cars_status",
        ]
        for idx in expected_indexes:
            assert any(idx in sql for sql in sqls), f"Index '{idx}' not dropped in downgrade"

    def test_downgrade_drops_cars_table(self, cars_migration):
        mock_op = MagicMock()
        with patch.object(cars_migration, "op", mock_op):
            cars_migration.downgrade()

        sqls = [c[0][0] for c in mock_op.execute.call_args_list]
        assert any("DROP TABLE IF EXISTS cars" in sql for sql in sqls)
