# uv add "pwdlib[argon2]"
# modern python library for some hashing stuff
# won the password hashing competition in 2015, and not another since
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlmodel import Session

from . import models
from .config import get_settings
from .database import get_session

ACCESS_TOKEN_EXPIRE_MINUTES = 60
JWT_ALGORITHM = "HS256"

# 2 side effects
# 1. **Header extraction.** FastAPI pulls the token out of the
#  header on protected routes; if there's no token,
#  the request gets rejected with a 401 before the handler runs.

# 2. **Docs UI integration.** The interactive `/docs` page sprouts
# an "Authorize" button that prompts for an email and password,
# posts them to the configured `tokenUrl`,
# and stores the returned token for subsequent requests.
security_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(
    token: Annotated[str, Depends(security_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> models.User:
    settings = get_settings()

    # not too specific credential exception
    # kind of a good thing, so hackers don't know why it failed
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
        )
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (InvalidTokenError, ValueError) as exc:
        raise credentials_exception from exc

    user = session.get(models.User, user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


# *, a, b, c, => anything after  * will need to feed in the keyword
def create_access_token(*, subject: str, expires_delta: timedelta | None = None) -> str:
    expires_at = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )  # or is cool, cause it's not ||
    payload = {
        "sub": subject,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        # get_secret_value(): unwraps the SecretStr and gives you back
        # the real str
        get_settings().jwt_secret_key.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )


# a configured hasher with sensible defaults.
password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    # hash the password (plain text) and return it
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # hash the plain_password and compare to hashed_password in db
    return password_hash.verify(plain_password, hashed_password)
