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

-----

### Model inheritance

Pydantic model can also be inherited.

For example,

```python
from pydantic import BaseModel

class PostCreate(PostBase):
    pass
```

Here, we inherited the attributes from the `PostBase` Pydantic model into the `PostCreate` model.

And, Pydantic only reads, JSON format data, that looks like dictionary, so in order to make it read data in form of attribute/object we use:

```python
from pydantic import BaseModel, ConfigDict, Field

class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes = True)

    id: int
    date_posted: str
```

`ConfigDict()` is used to make the Pydantic model class read values from attributes/objects too, otherwise it only reads the JSON, dictionary-like data.

----

### Returning a formatted response

If you want to return a response in a particular format, then `response_model` parameter is used in the _route decorator_.

For example,

```python
@app.get("/api/posts", response_model = list[PostResponse])
def get_posts():
    return posts
```

`response_model` says before sending data to the client, make sure every item looks like `PostResponse`.

What this says, is that, return a list of posts, where each post follows the PostResponse schema.

Another example where this is useful:

```python
# post data in form of list of dictionaries
posts = [
    {
        "id": 1,
        "title": "AI",
        "content": "Learning FastAPI",
        "secret_admin_note": "Don't show this"
    }
]

# schema
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
```

What you'll get as output is:

```python
[
    {
        "id": 1,
        "title": "AI",
        "content": "Learning FastAPI"
    }
]
```

As you noticed, `secret_admin_note` from post data is not returned in the output.

This is what schemas used for.

----

For validating incoming data, we use, in the function:

```python
post: PostCreate
```

For validating outgoing/response data, we use this, in the route decorator.

```python
response_model = PostResponse
```

