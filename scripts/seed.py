from sqlmodel import Session

from release_tracker.database import get_engine
from release_tracker.models import Project


def seed() -> None:
    # 1. Create a Session using the engine
    with Session(get_engine()) as session:
        # 2. Instantiate three Project objects
        frontend = Project(name="Frontend Redesign", slug="frontend-redesign")
        api = Project(name="API v2", slug="api-v2")
        db_migration = Project(name="Database Migration", slug="database-migration")

        # 3. Add them to the session
        session.add(frontend)
        session.add(api)
        session.add(db_migration)

        # 4. Commit the transaction to save them to the database
        session.commit()

        print("Loaded sample data for 3 projects.")


if __name__ == "__main__":
    seed()
