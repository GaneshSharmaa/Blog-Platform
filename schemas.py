# importing modules
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(min_length = 1, max_length = 20)
    email: EmailStr = Field(max_length = 120)

class UserCreate(UserBase):
    password: str = Field(min_length = 8)

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes = True)
    username: str
    id: int
    image_file: str | None
    image_path: str

class UserPrivate(UserPublic):
    email: EmailStr
class UserUpdate(BaseModel):
    username: str | None = Field(default = None, min_length = 1, max_length = 25)
    email: EmailStr | None = Field(default = None, max_length = 120)

class Token(BaseModel):
    access_token: str
    token_type: str

# creating a base field validation Pydantic model
class PostBase(BaseModel):
    title: str = Field(min_length = 1, max_length = 100)
    content: str = Field(min_length = 1)

# creating a Pydantic model for validating created post
# inheriting the PostBase Pydantic model
class PostCreate(PostBase):
    pass

# creating a Pydantic model for updating a post
class PostUpdate(BaseModel):
    title: str | None = Field(default = None, min_length = 1, max_length = 100)
    content: str | None = Field(default = None, min_length = 1)

# creating a Pydantic model for validating a post response
# inheriting the PostBase Pydantic model
# and configuring to read the attributes, not by default JSON
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes = True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserPublic

