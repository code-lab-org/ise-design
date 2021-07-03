from fastapi_users import models
from pydantic import Field
from typing import Optional

class User(models.BaseUser):
    name: Optional[str] = Field(
        None,
        description="User name."
    )

class UserCreate(models.BaseUserCreate):
    passcode: str = Field(
        ...,
        description="Registration pass code."
    )
    name: Optional[str] = Field(
        None,
        description="User name."
    )

class UserUpdate(User, models.BaseUserUpdate):
    pass

class UserDB(User, models.BaseUserDB):
    pass
