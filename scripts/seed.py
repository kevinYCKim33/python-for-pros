from datetime import UTC, date, datetime, timedelta

from sqlmodel import Session, delete

from release_tracker.database import get_engine
from release_tracker.models import Project, Task, TaskPriority, TaskStatus


def seed() -> None:
    today = datetime.now(UTC).date()
    # 1. Create a Session using the engine
    with Session(get_engine()) as session:
        # 1. clear db when running seed script
        session.exec(delete(Task))
        session.exec(delete(Project))
        session.commit()
        # 2. Instantiate three Project objects
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


if __name__ == "__main__":
    seed()
