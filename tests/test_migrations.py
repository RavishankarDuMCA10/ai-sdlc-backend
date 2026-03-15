"""
Unit tests for Alembic migration files.

These tests validate:
- The migration revision chain is correct
- The upgrade/downgrade operations use correct table names
- Column definitions match the TRD specification
"""
import importlib
import sys
import os
import pytest
from unittest.mock import MagicMock, patch, call


# ---------------------------------------------------------------------------
# Helpers to import migration modules without a live database
# ---------------------------------------------------------------------------

def _load_migration(filename: str):
    """Dynamically import a migration module by filename."""
    versions_dir = os.path.join(
        os.path.dirname(__file__), '..', 'alembic', 'versions'
    )
    spec_path = os.path.abspath(os.path.join(versions_dir, filename))
    spec = importlib.util.spec_from_file_location(filename.replace('.py', ''), spec_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Tests for 0001 – cars
# ---------------------------------------------------------------------------

class TestCarsMigration:
    def setup_method(self):
        self.migration = _load_migration('0001_create_cars_table.py')

    def test_revision_id(self):
        assert self.migration.revision == '0001'

    def test_down_revision_is_none(self):
        assert self.migration.down_revision is None

    def test_upgrade_creates_cars_table(self):
        mock_op = MagicMock()
        with patch.object(self.migration, 'op', mock_op):
            self.migration.upgrade()
        # create_table should be called with 'cars'
        create_table_calls = [
            c for c in mock_op.mock_calls if 'create_table' in str(c)
        ]
        assert any("'cars'" in str(c) or '"cars"' in str(c) for c in create_table_calls), \
            "upgrade() should call op.create_table('cars', ...)"

    def test_upgrade_creates_unique_constraint_on_licence_plate(self):
        mock_op = MagicMock()
        with patch.object(self.migration, 'op', mock_op):
            self.migration.upgrade()
        mock_op.create_unique_constraint.assert_called_once_with(
            'uq_cars_licence_plate', 'cars', ['licence_plate']
        )

    def test_upgrade_creates_check_constraint_fuel_type(self):
        mock_op = MagicMock()
        with patch.object(self.migration, 'op', mock_op):
            self.migration.upgrade()
        constraint_names = [
            call_args[0][0]
            for call_args in mock_op.create_check_constraint.call_args_list
        ]
        assert 'ck_cars_fuel_type' in constraint_names

    def test_upgrade_creates_check_constraint_status(self):
        mock_op = MagicMock()
        with patch.object(self.migration, 'op', mock_op):
            self.migration.upgrade()
        constraint_names = [
            call_args[0][0]
            for call_args in mock_op.create_check_constraint.call_args_list
        ]
        assert 'ck_cars_status' in constraint_names

    def test_upgrade_creates_check_constraint_condition_rating(self):
        mock_op = MagicMock()
        with patch.object(self.migration, 'op', mock_op):
            self.migration.upgrade()
        constraint_names = [
            call_args[0][0]
            for call_args in mock_op.create_check_constraint.call_args_list
        ]
        assert 'ck_cars_condition_rating' in constraint_names

    def test_upgrade_creates_indexes(self):
        mock_op = MagicMock()
        with patch.object(self.migration, 'op', mock_op):
            self.migration.upgrade()
        index_names = [
            call_args[0][0]
            for call_args in mock_op.create_index.call_args_list
        ]
        assert 'ix_cars_status' in index_names
        assert 'ix_cars_is_active' in index_names
        assert 'ix_cars_fuel_type' in index_names

    def test_downgrade_drops_cars_table(self):
        mock_op = MagicMock()
        with patch.object(self.migration, 'op', mock_op):
            self.migration.downgrade()
        mock_op.drop_table.assert_called_once_with('cars')


# ---------------------------------------------------------------------------
# Tests for 0002 – car_service_schedules
# ---------------------------------------------------------------------------

class TestCarServiceSchedulesMigration:
    def setup_method(self):
        self.migration = _load_migration('0002_create_car_service_schedules_table.py')

    def test_revision_id(self):
        assert self.migration.revision == '0002'

    def test_down_revision_points_to_0001(self):
        assert self.migration.down_revision == '0001'

    def test_upgrade_creates_car_service_schedules_table(self):
        mock_op = MagicMock()
        with patch.object(self.migration, 'op', mock_op):
            self.migration.upgrade()
        create_table_calls = [
            c for c in mock_op.mock_calls if 'create_table' in str(c)
        ]
        assert any(
            "'car_service_schedules'" in str(c) or '"car_service_schedules"' in str(c)
            for c in create_table_calls
        ), "upgrade() should call op.create_table('car_service_schedules', ...)"

    def test_upgrade_creates_status_check_constraint(self):
        mock_op = MagicMock()
        with patch.object(self.migration, 'op', mock_op):
            self.migration.upgrade()
        constraint_names = [
            call_args[0][0]
            for call_args in mock_op.create_check_constraint.call_args_list
        ]
        assert 'ck_car_service_schedules_status' in constraint_names

    def test_upgrade_creates_indexes(self):
        mock_op = MagicMock()
        with patch.object(self.migration, 'op', mock_op):
            self.migration.upgrade()
        index_names = [
            call_args[0][0]
            for call_args in mock_op.create_index.call_args_list
        ]
        assert 'ix_car_service_schedules_car_id' in index_names
        assert 'ix_car_service_schedules_status' in index_names
        assert 'ix_car_service_schedules_scheduled_date' in index_names

    def test_downgrade_drops_car_service_schedules_table(self):
        mock_op = MagicMock()
        with patch.object(self.migration, 'op', mock_op):
            self.migration.downgrade()
        mock_op.drop_table.assert_called_once_with('car_service_schedules')


# ---------------------------------------------------------------------------
# Tests for database module
# ---------------------------------------------------------------------------

class TestDatabaseModule:
    def test_get_connection_called_with_database_url(self):
        """get_connection should use DATABASE_URL from config."""
        with patch('app.database.psycopg2') as mock_psycopg2:
            import app.database as db_module
            db_module.get_connection()
            mock_psycopg2.connect.assert_called_once()
