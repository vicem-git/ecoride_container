from typing_extensions import Self
import re
from typing import List
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
    constr,
    UUID4,
)


class RegistrationData(BaseModel):
    email: EmailStr = Field(
        ...,
    )
    password: str = Field(
        ...,
    )
    confirm_password: str = Field(
        ...,
    )
    username: str = constr()
    roles: List[str] = Field(
        ...,
    )

    @field_validator("email")
    def validate_email(value):
        cleaned_email = value.strip().lower()
        if "@" not in cleaned_email or "." not in cleaned_email:
            raise ValueError("Veuillez fournir une adresse e-mail valide.")
        return cleaned_email

    @field_validator("username")
    def validate_username(value):
        min_length = 3
        max_length = 15
        cleaned_username = value.strip()
        if not re.match(r"^[a-zA-Z0-9_]+$", cleaned_username):
            raise ValueError(
                "Le nom d'utilisateur ne peut contenir que des lettres, des chiffres et des tirets bas."
            )
        if len(cleaned_username) < min_length or len(cleaned_username) > max_length:
            raise ValueError(
                f"Le nom d'utilisateur doit comporter entre {min_length} et {max_length} caractères."
            )
        return cleaned_username

    @field_validator("roles")
    def validate_roles(value):
        min_roles = 1
        if len(value) < min_roles:
            raise ValueError("Veuillez sélectionner au moins un rôle.")
        return value

    @field_validator("password")
    def validate_password(v):
        min_length = 8
        cleaned_password = v.strip()
        if len(cleaned_password) < min_length:
            raise ValueError(
                f"Le mot de passe doit comporter au moins {min_length} caractères."
            )
        return cleaned_password

    @model_validator(mode="after")
    def passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Les mots de passe ne correspondent pas.")
        return self


class LoginData(BaseModel):
    email: EmailStr = Field(
        ...,
    )
    password: str = Field(
        ...,
    )

    @field_validator("email")
    def validate_email(value):
        cleaned_email = value.strip().lower()
        if "@" not in cleaned_email or "." not in cleaned_email:
            raise ValueError("Veuillez fournir une adresse e-mail valide.")
        return cleaned_email

    @field_validator("password")
    def validate_password(value):
        min_length = 8
        cleaned_password = value.strip()
        if len(cleaned_password) < min_length:
            raise ValueError(
                f"Le mot de passe il comporte au moins {min_length} caractères."
            )
        return cleaned_password


# SEARCH FORMS ??
# WHAT OTHER FORMS ?
# search ? not needed id think
# vehicle add ?
# role edit
# review forms
# ??
