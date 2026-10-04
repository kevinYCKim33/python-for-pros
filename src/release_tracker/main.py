from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlmodel import Session

from . import crud
from .database import get_session
from .models import ProjectCreate, ProjectRead, ProjectUpdate

app = FastAPI(
    title="Release Tracker API",
    description="An API for tracking project milestones and developer tasks.",
)

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "app": "Release Tracker API",
        "docs": "/docs",
    }


@app.get("/projects", response_model=list[ProjectRead])
def list_projects(session: SessionDep):
    return crud.list_projects(session)


@app.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, session: SessionDep):
    project = crud.get_project(session, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@app.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    session: SessionDep,
):
    return crud.create_project(session, payload)


@app.patch("/projects/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    session: SessionDep,
):
    project = crud.get_project(session, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return crud.update_project(session, project, payload)


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, session: SessionDep):
    project = crud.get_project(session, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    crud.delete_project(session, project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
