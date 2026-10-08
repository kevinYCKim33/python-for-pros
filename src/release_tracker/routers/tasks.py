from typing import Annotated, Any

from fastapi import APIRouter, Query, Response, status

from release_tracker import crud
from release_tracker.dependencies import ProjectDep, SessionDep, TaskDep
from release_tracker.models import (
    TaskCreate,
    TaskPriority,
    TaskRead,
    TaskStatus,
    TaskUpdate,
)

# why no prefix="/tasks" ?
# list_tasks is GET /tasks, but create_task is POST /projects/{project_id}/tasks.
# Two of the routes start with /projects, three start with /tasks.
# A single router prefix would force the path on every route, which doesn't fit.
# We drop the prefix and write the full paths in each decorator.
router = APIRouter(tags=["tasks"])


@router.get("/tasks", response_model=list[TaskRead])
def list_tasks(
    session: SessionDep,
    # rest are query params, done via *
    project_id: int | None = None,
    project_slug: str | None = None,
    # can query by ?status="in_progress"
    task_status: Annotated[TaskStatus | None, Query(alias="status")] = None,
    # can query by ?priority="urgent"
    task_priority: Annotated[TaskPriority | None, Query(alias="priority")] = None,
    overdue_only: bool = False,
) -> Any:
    return crud.list_tasks(
        session,
        project_id=project_id,
        project_slug=project_slug,
        task_status=task_status,
        task_priority=task_priority,
        overdue_only=overdue_only,
    )


@router.post(
    "/projects/{project_id}/tasks/",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task(project: ProjectDep, payload: TaskCreate, session: SessionDep) -> Any:
    assert project.id is not None  # it'd just be project.id! in JS
    return crud.create_task(session, project.id, payload)


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task: TaskDep) -> Any:
    return task


# this has no status_code ??
# default in FastAPI is 200; which it should be for PATCH
@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(task: TaskDep, payload: TaskUpdate, session: SessionDep) -> Any:
    return crud.update_task(session, task, payload)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task: TaskDep, session: SessionDep) -> Response:
    crud.delete_task(session, task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
