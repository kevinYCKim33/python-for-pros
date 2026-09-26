import pytest

from slug import slugify


# must start out with test_
# then just describe the tests directly in its name
def test_slugify_lowercases_and_dashes_spaces():
    assert slugify("Release Tracker") == "release-tracker"


def test_slugify_strips_outer_whitespace():
    assert slugify("  hello  ") == "hello"


def test_slugify_rejects_empty_string():
    with pytest.raises(ValueError, match="cannot be empty"):
        slugify("")
