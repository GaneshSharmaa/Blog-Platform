# importing modules
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(min_length = 1, max_length = 20)
    email: EmailStr = Field(max_length = 120)

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes = True)

    id: int
    image_file: str | None
    image_path: str

# creating a base field validation Pydantic model
class PostBase(BaseModel):
    title: str = Field(min_length = 1, max_length = 100)
    content: str = Field(min_length = 1)

# creating a Pydantic model for validating created post
# inheriting the PostBase Pydantic model
class PostCreate(PostBase):
    user_id: int    # TEMPORARY

# creating a Pydantic model for validating a post response
# inheriting the PostBase Pydantic model
# and configuring to read the attributes, not by default JSON
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes = True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserResponse
