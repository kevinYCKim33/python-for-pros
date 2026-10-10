from datetime import UTC, datetime

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .models import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    Task,
    TaskCreate,
    TaskPriority,
    TaskStatus,
    TaskUpdate,
)


def slugify(value: str) -> str:
    cleaned = "".join(c for c in value.lower() if c.isalnum() or c == " ")
    return "-".join(cleaned.split()) or "project"


def list_projects(session: Session) -> list[Project]:
    statement = select(Project).order_by(Project.name)
    return list(session.exec(statement).all())


def get_project(session: Session, project_id: int) -> Project | None:
    return session.get(Project, project_id)


def create_project(session: Session, payload: ProjectCreate) -> Project:
    project = Project.model_validate(payload, update={"slug": slugify(payload.name)})
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def update_project(session: Session, project: Project, payload: ProjectUpdate) -> Project:
    updated_fields = payload.model_dump(exclude_unset=True)
    project.sqlmodel_update(updated_fields)

    if "name" in updated_fields and updated_fields["name"] is not None:
        project.slug = slugify(updated_fields["name"])

    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def delete_project(session: Session, project: Project) -> None:
    session.delete(project)
    session.commit()


def list_tasks(
    session: Session,
    # star separator =>
    # everything after must be named by keyword
    *,
    project_id: int | None = None,
    project_slug: str | None = None,
    task_status: TaskStatus | None = None,
    task_priority: TaskPriority | None = None,
    overdue_only: bool = False,
) -> list[Task]:
    # feels weird cause the ini. statement = seems to almost run after the if statement runs
    # It's like ordering at a restaurant: you can say "and a dessert after"
    # before you finish ordering your main course.
    # You're describing the whole meal, and the kitchen still
    # serves it in the right order.

    # Make two queries
    # 1. SELECT ... FROM tasks WHERE status = 'done'
    # 2. SELECT ... FROM projects WHERE id IN (...the project_ids from those tasks...)
    statement = select(Task).options(selectinload(Task.project))  # type: ignore[arg-type]

    # subtle note: it's not elif cause we can keep building on top of multiple queries
    if project_id is not None:
        statement = statement.where(Task.project_id == project_id)
    if project_slug is not None:
        statement = statement.join(Project).where(Project.slug == project_slug)
    if task_status is not None:
        statement = statement.where(Task.status == task_status)
    if task_priority is not None:
        statement = statement.where(Task.priority == task_priority)
    # lowkey kind of complex query since there's no is_overdue column in SQL
    if overdue_only:
        statement = statement.where(
            Task.due_date != None,  # noqa: E711
            Task.due_date < datetime.now(UTC).date(),  # type: ignore[operator]
            Task.status != TaskStatus.done,
        )

    return list(session.exec(statement).all())


def get_task(session: Session, task_id: int) -> Task | None:
    statement = (
        select(Task)
        # almost a pointless selectinload / eager loading
        # .options(selectinload(Task.project))  # type: ignore[arg-type]
        .where(Task.id == task_id)
    )
    return session.exec(statement).first()


def create_task(session: Session, project_id: int, payload: TaskCreate) -> Task:
    task = Task.model_validate(payload, update={"project_id": project_id})
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def update_task(session: Session, task: Task, payload: TaskUpdate) -> Task:
    # model_dump() takes payload into a dict
    # exclude_unset=True => only include fields client sent
    task.sqlmodel_update(payload.model_dump(exclude_unset=True))
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(session: Session, task: Task) -> None:
    session.delete(task)
    session.commit()
