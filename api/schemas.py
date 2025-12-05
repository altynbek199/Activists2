from pydantic import BaseModel, EmailStr, field_validator, Field
import uuid
from datetime import datetime
from db.models import PortalRole
from typing import Annotated
import re


NAME_REGEX = re.compile(r"^[а-яА-ЯёЁәәғғққңңөөұұүүһһііІІa-zA-Z0-9]+$", re.IGNORECASE)

class UserAddDTO(BaseModel):
    name: Annotated[str, Field(..., min_length=5)]
    email: EmailStr
    hashed_password: str

    @field_validator("name")
    def validate_name(cls, value: str):
        if not NAME_REGEX.fullmatch(value.strip()):
            raise ValueError(
                "Name should contains only rus, eng, kaz letters and digits"
            )
        return value

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
    def validate_name(cls, value: str):
        if not NAME_REGEX.fullmatch(value.strip()):
            raise ValueError(
                "Name should contains only rus, eng, kaz letters and digits"
            )
        return value


####################
# LOGIN
####################
class Token(BaseModel):
    access_token: str
    token_type: str


###################
# Events
###################

class EventAddDTO(BaseModel):
     title: str
     text: str
     author_id: uuid.UUID 
     photo: str | None = None

class EventShowDTO(EventAddDTO):
    event_id: uuid.UUID
    likes: int 
    created_at: datetime
    updated_at: datetime

class DeleteEventResponse(BaseModel):
    deleted_event_id: uuid.UUID     








