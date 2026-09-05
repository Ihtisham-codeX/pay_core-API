from pydantic import BaseModel, EmailStr
from datetime import datetime



class UserResponse(BaseModel):
    id:         int
    email:      str
    username:   str
    first_name: str
    last_name:  str
    phone:      str | None
    role:       str
    status:     str
    created_at: datetime


class UpdateProfileRequest(BaseModel):
    first_name: str | None = None
    last_name:  str | None = None
    phone:      str | None = None
