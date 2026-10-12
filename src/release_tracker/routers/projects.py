from fastapi import APIRouter, Response, status

from .. import crud
from ..dependencies import CurrentUserDep, ProjectDep, SessionDep
from ..models import Project, ProjectCreate, ProjectRead, ProjectUpdate

# tags: used in docs view to group displays
router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def list_projects(session: SessionDep) -> list[Project]:
    # our DB session is automatically injected and managed
    return crud.list_projects(session)


@router.get("/{project_id}", response_model=ProjectRead)
# FastAPI sees that ProjectDep has a Depends(get_project_or_404)
# so it executes that first
# it sees the project_id matches the {project_id}
# it also sees get_project_or_404 has a Depends(get_session)
# so it executes that first
# almost like a before_action in Rails
def get_project(project: ProjectDep) -> Project:
    return project


# any route that needs POSTs that need auth, tack on CurrentUserDep
@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate, session: SessionDep, current_user: CurrentUserDep
) -> Project:
    return crud.create_project(session, payload)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    current_user: CurrentUserDep,
    project: ProjectDep,
    payload: ProjectUpdate,
    session: SessionDep,
) -> Project:
    return crud.update_project(session, project, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    current_user: CurrentUserDep, project: ProjectDep, session: SessionDep
) -> Response:
    crud.delete_project(session, project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
