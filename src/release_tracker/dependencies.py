from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from .database import get_session

# Create a reusable dependency type
# magic line that anchors to the database
# how Python is able to talk to SQL
SessionDep = Annotated[Session, Depends(get_session)]
