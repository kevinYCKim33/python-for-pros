from datetime import UTC, datetime
from typing import Annotated

from pydantic import StringConstraints

# claude: should probably explicitly add sqlalchemy though sqlmodel implicitly
# imports it
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel  # Field comes from sqlmodel, not pydantic


def utc_now() -> datetime:
    return datetime.now(UTC)


# also reusable for stripping whitespace
ProjectName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2),
]


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
