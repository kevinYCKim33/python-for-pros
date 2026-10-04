from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlmodel import Session, select

from .database import get_session
from .models import Project, ProjectCreate, ProjectRead, ProjectUpdate


# In production, use a library like python-slugify to handle special cases like unicode and more.
# You'll also need to validate the slug doesn't already exist when updating and creating Projects.
def slugify(value: str) -> str:
    cleaned = "".join(c for c in value.lower() if c.isalnum() or c == " ")
    return "-".join(cleaned.split()) or "project"


app = FastAPI(
    title="Release Tracker API",
    description="An API for tracking project milestones and tasks for devs.",
)

SessionDep = Annotated[Session, Depends(get_session)]


# just some helpful "link" at / so users don't see 404
@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "app": "Release Tracker API",
        "docs": "/docs",
        "health": "/health",
    }


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


@app.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    session: SessionDep,
):
    # Project does inherit from SQLModel
    # Hey validate that with the payload from the FE, and this slugified field are correct
    project = Project.model_validate(payload, update={"slug": slugify(payload.name)})
    session.add(project)
    session.commit()
    session.refresh(project)  # so we can get the generated key id and created_at timestamp
    return project


@app.patch("/projects/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    session: SessionDep,
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # exclude_unset=True ensures we only update fields the client explicitly sent in their request.
    updated_fields = payload.model_dump(exclude_unset=True)
    project.sqlmodel_update(updated_fields)

    if "name" in updated_fields and updated_fields["name"] is not None:
        project.slug = slugify(updated_fields["name"])

    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    session.delete(project)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
