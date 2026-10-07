from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import StringConstraints

# claude: should probably explicitly add sqlalchemy though sqlmodel implicitly
# imports it
from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel  # Field comes from sqlmodel, not pydantic


def utc_now() -> datetime:
    return datetime.now(UTC)


# also reusable for stripping whitespace
ProjectName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2)]


# Why this in 1 step...
# class Book(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     title: str = Field(index=True)
#     author: str
#     pages: int | None = Field(default=None)


# But this done in 2?
# Claude Answer: payoff comes when you're typing API response types
# will be reused in reading, creating, and updating responses
# more flexibility
class ProjectBase(SQLModel):
    name: ProjectName = Field(unique=True)
    description: str | None = None


# this one seems a lot more associated with SQL side of things; id, created_at, tablename
class Project(ProjectBase, table=True):
    # name and description get inherited this way
    __tablename__ = "projects"  # can specify if we want to

    id: int | None = Field(default=None, primary_key=True)  # proj not saved could be None
    slug: str = Field(unique=True)  # don't want 2 proj with same slug

    # also need to have back_populates
    tasks: list[Task] = Relationship(back_populates="project")

    created_at: datetime = Field(
        default_factory=utc_now,  # function to call for every NEW row
        # sa for SqlAlchemy
        # dropping down to the SQLAlechmy land
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class ProjectCreate(ProjectBase):
    pass  # get exactly everything from ProjectBase straight up


class ProjectUpdate(SQLModel):
    name: ProjectName | None = None  # when we update, the name doesn't have to be unique
    description: str | None = None


class ProjectRead(ProjectBase):
    id: int
    slug: str
    created_at: datetime


class TaskStatus(StrEnum):
    planned = "planned"
    in_progress = "in_progress"
    blocked = "blocked"
    done = "done"


class TaskPriority(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


TaskTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2),
]


# TaskBase: everything minus all the SQL-y fields (foreign id, id)
class TaskBase(SQLModel):
    title: TaskTitle
    details: str | None = None  # details are optional
    status: TaskStatus = TaskStatus.planned
    priority: TaskPriority = TaskPriority.medium
    due_date: date | None = None
    # not datetime; if someone says due 10/15; no need to be super anal


class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    # table-only fields
    # fields that just pertain to the SQL-y part
    id: int | None = Field(default=None, primary_key=True)
    # a task will belong to a project_id
    # index = True
    # like if you ask give me all tasks from project 5
    # it will be indexed that project 5 has tasks 1, 4, and 7 w/o looking it all up
    project_id: int = Field(foreign_key="projects.id", index=True)

    project: Project = Relationship(back_populates="tasks")


# what back_populates buys me
# task = Task(title="Write docs")
# task.project = my_project
# print(task in my_project.tasks)  # True, already synced

# my_project.tasks.append(other_task)
# print(other_task.project is my_project)  # True


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: TaskTitle | None = None
    details: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None


class TaskRead(TaskBase):
    id: int
    project_id: int
