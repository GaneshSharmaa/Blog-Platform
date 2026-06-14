# FastAPI — Database Integretion

Until, now we were storing the posts data into a list of dictionaries, which lived in the memory. The moment the server stopped, all the post disappeared.

It won't happen now as we will store in the real database.

How's everything gonna work in short:

```plaintext
FastAPI
    ↓
SQLAlchemy
    ↓
SQLite Database
```

Creating a new file, specifically for the database, this is good practice in Software Development.

This file's job is to:

* Connect to a database
* Create database session
* Provide sessions to route
* Create a base class for models

----

### Step 1: Importing the module

```python
# importing modules
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
```

These are SQLAlchemy tools.

`create_engine` is used to create a connection to the database.

`sessionmaker` is used to create database sessions. Think session as conversation with the database.

`DeclarativeBase` it is used to create database models. This tells the SQLAlchemy, this class represents a database table.

### Step 2: Database URL

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"
```

This tells the SQLAlchemy, where is my database.

`sqlite:///` means use SQLite database.

`./blog.db` means create blog.db in current directory.

### Step 3: Creating an engine

```python
engine = create_engine(
    url = SQLALCHEMY_DATABASE_URL,
    connect_args = {"check_same_thread": False}
)
```

Think of engine as a bridge between Python ↔ database. Without it, there won't be any communication.

`"check_same_thread": False` tells the FastAPI to use multiple requests. Normally SQLite uses only one thread for connection.

### Step 4: Session factory

```python
SessionLocal = sessionmaker(
    autoflush = False,
    autocommit = False,
    bind = engine
)
```

Creates a session factory. Think of it as sessionmaker → creates session.

Every request gets new session.

`bind = engine` means connect sessions to this engine. Without engine, session won't know which database to run.

`autocommit = False` means don't save automatically. Need to do `db.commit()` explicitly to save.

`autoflush = False` means turning off sending the pending changes to database.

### Step 5: Base class

```python
class Base(DeclarativeBase):
    pass
```

SQLAlchemy sees post table, and creates database table.

### Step 6: Database dependency

```python
def get_db():
    with SessionLocal() as db:
        yield db
```

`db = SessionLocal()` creates database session, and now `db.query(...)`, `db.add(...)`, and `db.commit(...)`, can be used.

`yield` is FastAPI's dependency injection.

----

### Request flow

Suppose a user visits:

```
GET /api/posts
```

FastAPI:

```
Request arrives
    ↓
get_db()
    ↓
Create session
    ↓
Route gets db object
    ↓
Query database
    ↓
Return response
    ↓
Session closes
```

### SQLAlchemy ORM

**ORM → Object Relational Mapping**

Creating a new file `models.py`, this file is for creating SQLAlchemy ORM model file.

```plaintext
Python Classes
       ↓
SQLAlchemy ORM
       ↓
Database Tables
```

So, instead of writing the SQL manually, here we defined a Python class and SQLAlchemy creates/manages the table.

In this table, we define two database tables.
_User_ and _Post_.

The relationship between them is

```plaintext
One user
    ↓
Many posts
```

This is one-to-many relationship.

----

Let us see, how everything works here, step-by-step.

### Step #1: Imports

```python
from __future__ import annotations
from datetime import UTC, datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
```

Here, `__future__ module allows referencing classes before they even exists.

`datetime` is just imports for date and time.

In `sqlalchemy`, `DateTime`, `ForeignKey`, `Integer`, `String`, `Text` represent database column types.

`sqlalchemy.orm` module is for ORM imports.

`id: Mapped[int]` is same as `id: int` but for ORM.

`mapped_column(Integer)` means create database column accepting Integer value.

`relationship` is used for connecting tables.

### Step #2: Creating user table

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    username: Mapped[str] = mapped_column(String(50), unique = True, nullable = False)
    email: Mapped[str] = mapped_column(String(120), unique = True, nullable = False)
    image_file: Mapped[str | None] = mapped_column(String(200), nullable = True, default = None)
    
    posts: Mapped[list[Post]] = relationship(back_populates = "author")
```

`Base` is the class in the `database.py` file and here, we directly inherited it.

`__tablename__` means create a new table named `users`.

`id...` means this field stores an integer and `mapped_column()` tells to create database column, where `primary_key = True` means this is a primary key. `index = True` means creating an index for this column.

`String(50)` means maximum 50 characters.

`unique = True` means no duplicate values allowed, database rejects duplicates.

`nullable = False` means this cannot be empty.

In `image_file: Mapped[str | None]` means it could be anything a _string_ or _None_. `default = None` means if nothing provided store _None_.

In `posts: Mapped[list[Post]]` this means that it accepts multiple posts. This tells us that a user can have multiple posts.

So, if sometypes `user.posts` then a list of posts will be returned.

And, `relationship()` connects `user.posts` to the `post.author`.

`@property` this converts a method into an attribute. So, earlier you'd write `user.image_path()` and after you'd write `user.image_path`. Looks like variable, but runs a function.

In `content:...` line, the `Text` means this could be long, so we wrote `Text` and not `String(...)`.

And, `ForeignKey("users.id")` means every post belongs to a user.

And in `author:...`, `Mapped[User]`, means each post has exactly one author. And, `back_populates = "posts"` links back to `User.posts`

This creates two-way connection.

### Visual representation

```plaintext
users table
+----+----------+----------------+
| id | username | email          |
+----+----------+----------------+
| 1  | Ganesh   | abc@gmail.com  |
| 2  | John     | xyz@gmail.com  |
+----+----------+----------------+

             ▲
             │
             │ Foreign Key
             │
posts table
+----+----------------+---------+
| id | title          | user_id |
+----+----------------+---------+
| 1  | FastAPI        |    1    |
| 2  | SQLAlchemy     |    1    |
| 3  | Python Tips    |    2    |
+----+----------------+---------+
```
