from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# postgresql+psycopg://release_tracker:release_tracker@localhost:5432/release_tracker
# └──────┬─────────┘   └──────┬──────┘ └──────┬──────┘ └───┬───┘ └┬─┘ └──────┬──────┘
#  database + driver       username        password        host   port   database name

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://release_tracker:release_tracker@localhost:5432/release_tracker"
)


class Settings(BaseSettings):
    # 1. database_url => checks to see if DATABASE_URL exists in environment variable (i.e. export DATABASE_URL)
    # 2. if not, check to see if it exists in .env as DATABASE_URL
    # 3. if not, go with DEFAULT_DATABASE_URL
    database_url: str = DEFAULT_DATABASE_URL

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# ensures we build the settings object once and reuse it across the application.
# computed once, used forever
@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
