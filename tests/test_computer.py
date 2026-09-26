import pytest
from pydantic import ValidationError

from computer import Computer


def test_computer_valid():
    laptop = Computer(brand="apple", ram_gb=16, hard_drive_gb=512)
    assert laptop.brand == "apple"
    assert laptop.ram_gb == 16
    assert laptop.hard_drive_gb == 512


def test_computer_rejects_string_ram():
    with pytest.raises(ValidationError):
        Computer(brand="apple", ram_gb="thirty two", hard_drive_gb=512)


def test_computer_requires_brand():
    with pytest.raises(ValidationError):
        Computer(ram_gb=16, hard_drive_gb=1024)
