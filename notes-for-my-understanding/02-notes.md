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

### Pydantic schema design for data modeling

First, let's get clear on what is _schema_,\
A schema defines what data is expected, what data is allowed, what data should be returned.

Think of schema like a blueprint for data.

With Pydantic schemas, data automatically is validated.

And we use `Field` for field validation.

```python
from pydantic import Field, BaseModel

class PostBase(BaseModel):
    title: str = Field(
        min_length = 5
        max_length = 100
    )
    content: str = Field(
        min_length = 20
        max_length = 1500
    )
```

And, `BaseModel` that we inherit from, provides the:

* Validation
* Serialization
* Type conversion
* JSON support
* Swagger document support

Without, the `BaseModel`, the class is just another Python class, but it is Pydantic model.

And, `Field()`, we use is for validation rules.

### Schema inheritance

In order to avoid repeating fields, we use schema inheritance.

For example,

```python
class PostCreate(PostBase):
    pass
```

Here, we inherited the schema from the `PostBase` Pydantic model into the `PostCreate` model.

-----

### Request validation / input validation

For validating input data, we use, in the function:

```python
@app.post("/posts")
def create_post(post: PostCreate):
    new_post = {
        "author": post.author,
        "title": post.title,
        "content": post.content,
        "date_posted": "June 02, 2026"
    }
    posts.append(new_post)
    return new_post
```

Flow of the request/input validation:

```plaintext
Client sends JSON
    ↓
Pydantic validation
    ↓
Route executes
```

------

### Response validation / output validation

If you want to return a response in a particular format, then `response_model` parameter is used in the _route decorator_. This is called _Response Validation_ or _Output Validation_.

For example,

```python
@app.get("/api/posts", response_model = list[PostResponse])
def get_posts():
    return posts
```

`response_model` says before sending data to the client, make sure every item looks like `PostResponse`.

What this says, is that, return a _list of posts_, where each post follows the `PostResponse` schema. Meaning return a list where every item follows `PostResponse`.

`response_model` parameter defines response structure.

Flow of the response/output validation:

```plaintext
Route returns data
    ↓
Pydantic validates response
    ↓
Client receives validated JSON
```

Using this response/output validation, benefits us by removing unwanted fields, prevents invalid responses, and improves API docs.

-----

### Example of response/output validation:

Returned by route:

```python
{
    "id": 1,
    "title": "FastAPI",
    "secret": "hidden"
}
```

Response model:

```python
class PostResponse(BaseModel):
    id: int
    title: str
```

Client receives:

```python
{
    "id": 1,
    "title": "FastAPI"
}
```

`secret` removed automatically, because it was not in the response model.

----

### ConfigDict

```python
from pydantic import ConfigDict

class PostResponse(PostBase):

    model_config = ConfigDict(
        from_attributes=True
    )
```

The purpose is it allows Pydantic model for reading object attributes. Useful for database ORM and objects.

-----

### Entire Pydantic model flow

```plaintext
Client Request
       ↓
PostCreate Schema
(Input Validation)
       ↓
Route Function
(Business Logic)
       ↓
PostResponse Schema
(Output Validation)
       ↓
Client Response
```

