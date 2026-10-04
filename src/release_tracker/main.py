from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Session, select

from .database import get_session
from .models import Project, ProjectRead  # . means relative import

app = FastAPI(
    title="Release Tracker API",
    description="An API for tracking project milestones and tasks for devs.",
)

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/projects", response_model=list[ProjectRead])
def list_projects(session: SessionDep):
    statement = select(Project).order_by(Project.name)
    projects = session.exec(statement).all()  # .all() return all of the results
    return list(projects)


@app.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project
