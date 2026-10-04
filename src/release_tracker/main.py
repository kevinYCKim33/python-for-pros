from fastapi import FastAPI, Response, status

from . import crud
from .dependencies import ProjectDep, SessionDep
from .models import ProjectCreate, ProjectRead, ProjectUpdate

app = FastAPI(
    title="Release Tracker API",
    description="An API for tracking project milestones and developer tasks.",
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "app": "Release Tracker API",
        "docs": "/docs",
    }


@app.get("/projects", response_model=list[ProjectRead])
def list_projects(session: SessionDep):
    # our DB session is automatically injected and managed
    return crud.list_projects(session)


@app.get("/projects/{project_id}", response_model=ProjectRead)
# FastAPI sees that ProjectDep has a Depends(get_project_or_404)
# so it executes that first
# it sees the project_id matches the {project_id}
# it also sees get_project_or_404 has a Depends(get_session)
# so it executes that first
def get_project(project: ProjectDep):
    return project


@app.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    session: SessionDep,
):
    return crud.create_project(session, payload)


@app.patch("/projects/{project_id}", response_model=ProjectRead)
def update_project(
    project: ProjectDep,
    payload: ProjectUpdate,
    session: SessionDep,
):
    return crud.update_project(session, project, payload)


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project: ProjectDep, session: SessionDep):
    crud.delete_project(session, project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
