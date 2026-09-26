from pydantic import BaseModel, ValidationError


class Computer(BaseModel):
    brand: str
    ram_gb: int
    hard_drive_gb: int


laptop = Computer(brand="apple", ram_gb=16, hard_drive_gb=512)
print(laptop)  # brand='apple' ram_gb=16 hard_drive_gb=512


try:
    bad = Computer(brand="apple", ram_gb="thirty two", hard_drive_gb=512)
except ValidationError as e:
    print(e)

# 1 validation error for Computer
# ram_gb
#   Input should be a valid integer, unable to parse string as an integer
#     [type=int_parsing, input_value='thirty two', input_type=str]
#     For further information visit https://errors.pydantic.dev/2.13/v/int_parsing
