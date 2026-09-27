from fastapi import FastAPI
from pydantic import BaseModel


class ProjectRead(BaseModel):
    id: int
    name: str
    slug: str


app = FastAPI(title="Release Tracker API")


# A simple mock database for now
mock_database: dict[int, ProjectRead] = {
    1: ProjectRead(id=1, name="Frontend Redesign", slug="frontend-redesign"),
    2: ProjectRead(id=2, name="API v2", slug="api-v2"),
    3: ProjectRead(id=3, name="Database Migration", slug="database-migration"),
}


# how FastAPI handles a show page
@app.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
):  # FastAPI will auto-convert /projects/2 's "2" to 2
    # FastAPI will also auto throw a 422 if user does /projects/hello
    # for free! no need for error handler!
    return mock_database.get(project_id)


# how FastAPI handles queries in the search
# /projects?name=API+v2
@app.get("/projects", response_model=list[ProjectRead])
def list_projects(name: str | None = None):  # query parameters go here
    projects = list(
        mock_database.values()
    )  # mock_db.values() only iterable, needs to be explicitly converted to a list
    if name is None:
        return projects
    # cool way to filter via query parameters!
    return [p for p in projects if p.name == name]  #
