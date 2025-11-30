from pydantic import BaseModel, EmailStr, field_validator, Field
import uuid
from datetime import datetime
from db.models import PortalRole
from typing import Annotated

class UserAddDTO(BaseModel):
    name: str
    email: str
    hashed_password: str

    @field_validator("name")
    def validate_first_name(cls, value: str):
        if not value.isalnum():
            raise ValueError(
                detail="Name should contains only letters and digits"
            )


class UserShowDTO(UserAddDTO):
    user_id: uuid.UUID   
    created_at: datetime
    roles: list[PortalRole]

class DeleteUserResponse(BaseModel):
    deleted_user_id: uuid.UUID  

class UpdatedUserResponse(BaseModel):
    updated_user_id: uuid.UUID

class UpdateUserRequest(BaseModel):
    name: Annotated[str | None, Field(min_length=5)] = None
    email: EmailStr | None = None
    
    @field_validator("name")
    def validate_first_name(cls, value: str):
        if not value.isalnum():
            raise ValueError(
                detail="Name should contains only letters and digits"
            )

####################
# LOGIN
####################
class Token(BaseModel):
    access_token: str
    token_type: str







