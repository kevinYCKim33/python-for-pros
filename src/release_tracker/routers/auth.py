from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from release_tracker import crud, models
from release_tracker.dependencies import CurrentUserDep, SessionDep
from release_tracker.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


# NOTE: A production deployment should add rate limiting to this endpoint
# to guard against brute-force password attacks.
@router.post("/token")
def login_for_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> models.AccessToken:
    """OAuth2 compatible token login.

    Submit the email address as `username` and the password.
    """
    email = form_data.username.lower()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = crud.get_user_by_email(session, email)
    if user is None or not user.is_active:
        raise credentials_exception

    if not verify_password(form_data.password, user.hashed_password):
        raise credentials_exception

    access_token = create_access_token(subject=str(user.id))
    return models.AccessToken(access_token=access_token)


@router.post(
    "/register",
    response_model=models.UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: models.UserCreate, session: SessionDep) -> Any:
    return crud.create_user(session, email=payload.email, password=payload.password)


@router.get("/me", response_model=models.UserRead)
def read_current_user(current_user: CurrentUserDep) -> models.User:
    return current_user
