"""Database migration runner.

Provides a CLI wrapper around Alembic to apply or revert migrations
without requiring the ``alembic`` command to be on PATH.

Usage
-----
Apply all pending migrations (upgrade to head):
    python scripts/migrate.py

Apply migrations up to a specific revision:
    python scripts/migrate.py --revision 0001

Revert the most recent migration:
    python scripts/migrate.py --downgrade -1

Revert all migrations:
    python scripts/migrate.py --downgrade base

Show current migration state:
    python scripts/migrate.py --current

Show full migration history:
    python scripts/migrate.py --history
"""
import argparse
import os
import sys

from alembic import command
from alembic.config import Config


_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _alembic_config() -> Config:
    """Return an Alembic :class:`~alembic.config.Config` wired to the project root."""
    ini_path = os.path.join(_PROJECT_ROOT, "alembic.ini")
    cfg = Config(ini_path)
    # Ensure the project root is used as the base for the script location.
    cfg.set_main_option("script_location", os.path.join(_PROJECT_ROOT, "migrations"))
    return cfg


def upgrade(revision: str = "head") -> None:
    """Apply migrations up to *revision* (default: ``head``)."""
    cfg = _alembic_config()
    print(f"Applying migrations up to '{revision}' …")
    command.upgrade(cfg, revision)
    print("Done.")


def downgrade(revision: str) -> None:
    """Revert migrations down to *revision*."""
    cfg = _alembic_config()
    print(f"Reverting migrations to '{revision}' …")
    command.downgrade(cfg, revision)
    print("Done.")


def current() -> None:
    """Print the current migration revision."""
    cfg = _alembic_config()
    command.current(cfg, verbose=True)


def history() -> None:
    """Print the full migration history."""
    cfg = _alembic_config()
    command.history(cfg, verbose=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Alembic database migrations for the AI SDLC backend.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    action = parser.add_mutually_exclusive_group()
    action.add_argument(
        "--revision",
        metavar="REV",
        default="head",
        help="Upgrade to this revision (default: head)",
    )
    action.add_argument(
        "--downgrade",
        metavar="REV",
        help="Downgrade to this revision (e.g. -1, base, 0001)",
    )
    action.add_argument(
        "--current",
        action="store_true",
        help="Show the current migration revision and exit",
    )
    action.add_argument(
        "--history",
        action="store_true",
        help="Show the full migration history and exit",
    )

    args = parser.parse_args()

    try:
        if args.current:
            current()
        elif args.history:
            history()
        elif args.downgrade is not None:
            downgrade(args.downgrade)
        else:
            upgrade(args.revision)
    except Exception as exc:  # pragma: no cover  # noqa: BLE001
        # Broad catch is intentional: this is the CLI entry point and any
        # unhandled exception (Alembic CommandError, DB connection error, etc.)
        # should surface as a clean error message rather than a raw traceback.
        print(f"Migration failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
