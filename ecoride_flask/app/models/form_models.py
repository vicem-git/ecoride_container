from typing_extensions import Self
from typing import List
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    model_validator,
    constr,
    UUID4,
)


class RegistrationData(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password")
    confirm_password: str = Field(
        ..., min_length=8, description="Confirm user's password"
    )
    username: str = constr(min_length=3, max_length=30)
    roles: List[str] = Field(..., min_items=1)

    @model_validator(mode="after")
    def passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginData(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")
