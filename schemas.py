# importing modules
from pydantic import BaseModel, ConfigDict, Field

# creating a base field validation Pydantic model
class PostBase(BaseModel):
    title: str = Field(min_length = 1, max_length = 100)
    content: str = Field(min_length = 1)
    author: str = Field(min_length = 1, max_length = 50)

# creating a Pydantic model for validating created post
# inheriting the PostBase Pydantic model
class PostCreate(PostBase):
    pass

# creating a Pydantic model for validating a post response
# inheriting the PostBase Pydantic model
# and configuring to read the attributes, not by default JSON
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes = True)

    id: int
    date_posted: str
