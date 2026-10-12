import pytest
from pydantic import ValidationError

from release_tracker.config import Settings


def test_settings_validates_jwt_secret_length() -> None:
    # Explicitly passing a short key bypasses the environment variable lookup
    # and directly tests Pydantic's field validation logic without monkeypatching.
    with pytest.raises(ValidationError, match="at least 32"):
        Settings(jwt_secret_key="too-short")  # type: ignore[arg-type]
