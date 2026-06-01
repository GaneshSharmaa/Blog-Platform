# FastAPI — Pydantic

Pydantic is used for:

* Data validation
* Data parsing
* Type checking
* Serialization

Pydantic helps in validating request and response data.

For example,

```python
from pydantic import BaseModel

class PostBase(BaseModel):
    title: str
    content: str
```

These help in validating the data automatically. This will tell that `title` and `content` should always be string, if any other data type is passed then it won't be accepted.

Also, the `BaseModel` that we write in the class, is what differentiates the class from the normal Python class to a data model.

And, the class can also be inherited.

For example,

```python
from pydantic import BaseModel

class PostCreate(PostBase):
    pass
```

Here, we inherited the attributes from the `PostBase` Pydantic model class into the `PostCreate` model class.

And, Pydantic only accepts, JSON format data, that looks like dictionary, so in order to make it accept data in form of attribute, we use:

```python
from pydantic import BaseModel, ConfigDict, Field

class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes = True)

    id: int
    date_posted: str
```

`ConfigDict()` is used to make the Pydantic model class accept values from attributes too, otherwise it only accepts the JSON, dictionary-like data only.

