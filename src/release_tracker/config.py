import logging
from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# postgresql+psycopg://release_tracker:release_tracker@localhost:5432/release_tracker
# └──────┬─────────┘   └──────┬──────┘ └──────┬──────┘ └───┬───┘ └┬─┘ └──────┬──────┘
#  database + driver       username        password        host   port   database name

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://release_tracker:release_tracker@localhost:5432/release_tracker"
)
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


# where most stuff in here goes linked to .env file
# jwt_secret_key => .env's JWT_SECRET_KEY
class Settings(BaseSettings):
    # 1. database_url => checks to see if DATABASE_URL exists in environment variable (i.e. export DATABASE_URL)
    # 2. if not, check to see if it exists in .env as DATABASE_URL
    # 3. if not, go with DEFAULT_DATABASE_URL
    database_url: str = DEFAULT_DATABASE_URL

    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # SecretStr gets logged as *****
    # also of note, no default value stated
    # so if .env is missing JWT_SECRET_KEY, it just flat out won't start
    # intentional!
    jwt_secret_key: SecretStr = Field(min_length=32)


def configure_logging(*, debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format=LOG_FORMAT)


# ensures we build the settings object once and reuse it across the application.
# computed once, used forever
@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
