"""Unit tests for scripts/migrate.py."""
import sys
import os
from unittest.mock import MagicMock, patch, call

import pytest

# Allow importing from the project root without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import scripts.migrate as migrate_script


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_main(argv: list[str]):
    """Call migrate_script.main() with a given argv list."""
    with patch.object(sys, "argv", ["migrate.py"] + argv):
        migrate_script.main()


# ---------------------------------------------------------------------------
# _alembic_config
# ---------------------------------------------------------------------------

class TestAlembicConfig:
    def test_returns_config_with_correct_ini(self):
        """Config should point to alembic.ini in the project root."""
        cfg = migrate_script._alembic_config()
        assert cfg.get_main_option("script_location").endswith("migrations")


# ---------------------------------------------------------------------------
# upgrade / downgrade / current / history
# ---------------------------------------------------------------------------

class TestUpgrade:
    def test_upgrade_head(self, capsys):
        with patch("scripts.migrate.command") as mock_cmd, \
             patch("scripts.migrate._alembic_config") as mock_cfg:
            migrate_script.upgrade()
            mock_cmd.upgrade.assert_called_once_with(mock_cfg.return_value, "head")
        captured = capsys.readouterr()
        assert "head" in captured.out
        assert "Done" in captured.out

    def test_upgrade_specific_revision(self, capsys):
        with patch("scripts.migrate.command") as mock_cmd, \
             patch("scripts.migrate._alembic_config") as mock_cfg:
            migrate_script.upgrade("0001")
            mock_cmd.upgrade.assert_called_once_with(mock_cfg.return_value, "0001")
        captured = capsys.readouterr()
        assert "0001" in captured.out


class TestDowngrade:
    def test_downgrade_minus_one(self, capsys):
        with patch("scripts.migrate.command") as mock_cmd, \
             patch("scripts.migrate._alembic_config") as mock_cfg:
            migrate_script.downgrade("-1")
            mock_cmd.downgrade.assert_called_once_with(mock_cfg.return_value, "-1")
        captured = capsys.readouterr()
        assert "-1" in captured.out
        assert "Done" in captured.out

    def test_downgrade_base(self, capsys):
        with patch("scripts.migrate.command") as mock_cmd, \
             patch("scripts.migrate._alembic_config") as mock_cfg:
            migrate_script.downgrade("base")
            mock_cmd.downgrade.assert_called_once_with(mock_cfg.return_value, "base")


class TestCurrent:
    def test_current_calls_command(self):
        with patch("scripts.migrate.command") as mock_cmd, \
             patch("scripts.migrate._alembic_config") as mock_cfg:
            migrate_script.current()
            mock_cmd.current.assert_called_once_with(mock_cfg.return_value, verbose=True)


class TestHistory:
    def test_history_calls_command(self):
        with patch("scripts.migrate.command") as mock_cmd, \
             patch("scripts.migrate._alembic_config") as mock_cfg:
            migrate_script.history()
            mock_cmd.history.assert_called_once_with(mock_cfg.return_value, verbose=True)


# ---------------------------------------------------------------------------
# CLI (main)
# ---------------------------------------------------------------------------

class TestMain:
    def test_main_default_upgrades_to_head(self):
        with patch("scripts.migrate.upgrade") as mock_upgrade:
            _run_main([])
            mock_upgrade.assert_called_once_with("head")

    def test_main_revision_flag(self):
        with patch("scripts.migrate.upgrade") as mock_upgrade:
            _run_main(["--revision", "0001"])
            mock_upgrade.assert_called_once_with("0001")

    def test_main_downgrade_flag(self):
        with patch("scripts.migrate.downgrade") as mock_downgrade:
            _run_main(["--downgrade", "-1"])
            mock_downgrade.assert_called_once_with("-1")

    def test_main_current_flag(self):
        with patch("scripts.migrate.current") as mock_current:
            _run_main(["--current"])
            mock_current.assert_called_once()

    def test_main_history_flag(self):
        with patch("scripts.migrate.history") as mock_history:
            _run_main(["--history"])
            mock_history.assert_called_once()
