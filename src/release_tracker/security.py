# uv add "pwdlib[argon2]"
# modern python library for some hashing stuff
# won the password hashing competition in 2015, and not another since
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from .config import get_settings

ACCESS_TOKEN_EXPIRE_MINUTES = 60
JWT_ALGORITHM = "HS256"


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
