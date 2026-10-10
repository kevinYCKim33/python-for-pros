# uv add "pwdlib[argon2]"
# modern python library for some hashing stuff
# won the password hashing competition in 2015, and not another since
from pwdlib import PasswordHash

# a configured hasher with sensible defaults.
password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    # hash the password (plain text) and return it
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # hash the plain_password and compare to hashed_password in db
    return password_hash.verify(plain_password, hashed_password)
