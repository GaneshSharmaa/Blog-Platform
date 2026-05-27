# FastAPI

### Installing the FastAPI module

```bash
uv pip install fastapi[standard]
```

`fastapi[standard]` will also install all the other dependencies for this module like _uvicorn_, and more other dependencies.

### Running FastAPI

In order to run FastAPI app, you can use
```bash
fastapi dev app.py
```

You can also use `run` inplace of `dev`, but `dev` gives you automatic reload after each changes made, you don't have to start the server again and again.

### Importing the FastAPI module

In order to import **_FastAPI_**, you can import it by
```python
# importing the module
from fastapi import FastAPI

# initializing the server
app = FastAPI()
```

### Creating an end point

End point is where the users perform CRUD operations (CRUD stands for Create, Read, Update, Delete).

In order to create one
```python
# importing the module
from fastapi import FastAPI

# initializing the server
app = FastAPI()

# endpoint
@app.get("/")
def home():
    return "Hello World!"
```
