import argparse
from datetime import UTC, date, datetime, timedelta

from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlmodel import Session, delete, select

from release_tracker import crud
from release_tracker.database import get_engine
from release_tracker.models import Project, Task, TaskPriority, TaskStatus, User

SEED_USER_EMAIL = "demo@release-tracker.local"
SEED_USER_PASSWORD = "demo-password"


def seed(*, reset: bool = False) -> None:
    today = datetime.now(UTC).date()
    # 1. Create a Session using the engine
    with Session(get_engine()) as session:
        # 1. clear db only when asked to (uv run scripts/seed.py --reset)
        if reset:
            session.exec(delete(Task))
            session.exec(delete(Project))
            session.exec(delete(User))
            session.commit()
            print("Cleared existing project, task, and user data.")

        # without --reset, running seed twice would hit the unique constraints, so bail early
        if session.exec(select(Project.id).limit(1)).first() is not None:
            print("Sample project data already exists. Use --reset to reload it.")
            return

        # 2. Instantiate User
        crud.create_user(
            session,
            email=SEED_USER_EMAIL,
            password=SEED_USER_PASSWORD,
        )

        # 2a. Instantiate three Project objects
        frontend = Project(name="Frontend Redesign", slug="frontend-redesign")
        api = Project(name="API v2", slug="api-v2")
        db_migration = Project(name="Database Migration", slug="database-migration")
        # 3. Add them to the session
        session.add_all([frontend, api, db_migration])
        session.commit()
        # claude says these refresh are optional, as session.commit()
        # reloads the row automatically via SQLAlchemy
        session.refresh(frontend)
        session.refresh(api)
        session.refresh(db_migration)
        # MyPy typing quirks
        assert frontend.id is not None
        assert api.id is not None
        assert db_migration.id is not None

        tasks = [
            Task(
                title="Migrate auth flow to new design",
                project_id=frontend.id,
                status=TaskStatus.in_progress,
                priority=TaskPriority.high,
                due_date=today + timedelta(days=7),
            ),
            Task(
                title="Wire up the dashboard",
                project_id=frontend.id,
                status=TaskStatus.planned,
                priority=TaskPriority.medium,
            ),
            Task(
                title="Stabilize the v2 endpoints",
                project_id=api.id,
                status=TaskStatus.blocked,
                priority=TaskPriority.urgent,
                due_date=today - timedelta(days=2),
            ),
            Task(
                title="Backfill task data",
                project_id=db_migration.id,
                status=TaskStatus.done,
                priority=TaskPriority.low,
                due_date=date(2025, 12, 1),
            ),
        ]
        session.add_all(tasks)
        session.commit()

        print(f"Loaded sample data for 3 projects and {len(tasks)} tasks.")
        print(f"Demo user: {SEED_USER_EMAIL} / {SEED_USER_PASSWORD}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load sample data for Release Tracker.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing project, task, and user records before loading fresh sample data.",
    )
    arguments = parser.parse_args()
    # turn the two most common failures into a readable message instead of a stack trace
    try:
        seed(reset=arguments.reset)
    except ProgrammingError as exc:  # tables don't exist yet
        raise SystemExit(
            "Database tables are missing. Run `uv run alembic upgrade head` first."
        ) from exc
    except OperationalError as exc:  # can't reach Postgres at all
        raise SystemExit(
            "Could not connect to the database. Is the Postgres container running?"
        ) from exc
