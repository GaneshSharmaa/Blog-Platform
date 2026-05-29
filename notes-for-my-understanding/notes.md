# FastAPI

FastAPI is a web framework used to build APIs, backend services, and production-grade web applications.

There are other Python-based web frameworks too, like **Flask** and **Django**.

FastAPI provides:
- Very fast (built on ASGI)
- Uses Python type hints
- Automatic validation
- Automatic API docs
- Async support
- Easy integration with AI/ML

FastAPI creates automatic API documents. So no hassle of manually writing docs.

It could be accessed by adding `/docs` at the end of the URL that we get after running the server.

It would look something like this:
```bash
http://127.0.0.1:8000/docs
```

-----

### Installing the FastAPI module

```bash
uv pip install fastapi[standard]
```

`fastapi[standard]` will also install all the other dependencies for this module like _uvicorn_, and more other dependencies.

-------

### Running FastAPI

In order to run FastAPI app, you can use
```bash
fastapi dev app.py
```

You can also use `run` inplace of `dev`, but `dev` gives you automatic reload after each changes made, you don't have to start the server again and again.

--------

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

An endpoint is created using _decorators_. _Decorators_ are statements written with symbol `@`. While `"/"` represents the root directory. This is called **_routing_**.

Also, if you don't want a route to be added in the docs:
```python
@app.get("/pages", include_in_schema = False)
```

This way by using the `include_in_schema` parameter, this route won't be added into the docs.

------

### Jinja2 — For HTML Templates

FastAPI functions return JSON, but we don't want that, instead we want beautiful HTML pages, so we use _Jinja2 Templates_ for it.

**_Jinja2_** is used for templating HTML. Now, we are no longer using static plain HTML, we are using dynamic HTML.

_Jinja2_ lets Python inject data into the HTML file.

First a template is created
```python
# importing the modules
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request

# creating a HTML template
template = Jinja2Templates(directory = "./templates")
```

This tells the Python to look for HTML files in the `templates/` folder.

And now we will create a template response.
```python
from fastapi.templating 
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, name = "home.html", context = {"posts": posts})
```

`TemplateResponse()` needs `request` as its parameter, even though it is not used.

`TemplateResponse()` helps in returning HTML page, by default the FastAPI returns _JSON_.

`name = "home.html` parameter tells the FastAPI to render the HTML file that is provided into the `name` parameter.

`context = {"posts": posts}` this sends the Python data into the HTML.

The Python variable `posts = [...]` gets send into the template as posts.

Now, let's see the HTML file.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastAPI Blog</title>
</head>
<body>
    <h1>FastAPI Blog</h1>
    {% for post in posts %}
    <h2>{{ post.title }}</h2>
    <p>{{ post.content }}</p>
    {% endfor %}
</body>
</html>
```

The weird syntax in `{...}`, is Jinja2 syntax.

Here, `{{ }}` → print values.\
And `{% %}` → logic statements (such as if statements, loop statements, etc.).
```html
<h2>{{ post.title }}</h2>
```
Take `post.title` from Python and display it here.

Then, `{% endfor %}` → closes the loop.

And, `{# #}` → comments.

So, basically this weird looking syntax in HTML is just Jinja2 template syntax, which looks like Python and also behaves similarly.

------

### Folder structure and what it means

First, let's talk about the folder structure and why it is the it is?

### `home.html` — Page Content

This is the actual page content. This is the main HTML file that exists in the `templates` folder.

And, by using `{% extends "layout.html" %}`, we tell it to use `layout.html` as the parent template.

So, `home.html` inherits navbar, CSS, Bootstrap, overall structure from `layout.html`.

### `layout.html` — The Base Template

And, `layout.html` is the master design of your website. Things like:
- navbar
- footer
- Bootstrap
- Global CSS

Stuff that should appear on every page. Instead of repeating this on every HTML file, we write it once in `layout.html`.

And, by using:
```python
{% block content %}
...
{% endblock content %}
```

This, means that "this area will change depending on the page."

### Static Files — `static/` folder

This is very important as websites need CSS, JavaScript, images, icons, all along the website on every page. These are called as _static files_, because they don't change dynamically.

This is done, because it helps avoid writing 1000 lines of CSS, for each and every HTML file.

The `main.py` access this `static/` directory by using:
```python
# importing the module
from fastapi.staticfiles import StaticFiles

# static folder access to the FastAPI
app.mount(
    "/static",
    StaticFiles(directory = "static"),
    name = "static"
)
```

This tells the browser to go inside the `static/` folder.

The `mount()` method, makes a computer directory into a URL.

Let's understand the arguments of this method:
- `/static` → This is URL by which the server access the files.
- `StaticFiles(directory = "static")` → Tells to look into this folder.
- `name = "static"` → This is an internal label. This is for FastAPI to add in the `url_for`.

So, what this actually means is:\
"Whenever browser requests `/static/...`, go look inside my `static/` folder, and refer to this mounted folder internally as `'static'`."

When browser asks about:
```python
/static/css/main.css
```

FastAPI looks here:
```python
project/static/css/main.css
```
and, sends it.

And, the reason we mount the entire `static/` folder is then it can access the JS, images, means everything that's needed.

Now, for linking this:
```python
static/css/main.css
```

We, go to `layout.html` and add:
```python
<link
rel = "stylesheet"
href = "{{ url_for("static", path = "/css/main.css") }}
>
```
This loads the CSS file.

And, the reason we use `url_for` in above code, is it safer, if path changes later, then FastAPI updates the URL automatically.

-----

### Understanding the flow

```
User visits 'localhost:8000'
        ↓
FastAPI route runs 'def home()'
        ↓
'posts' sends the data to 'home.html'
        ↓
'home.html' injects the content into 'layout.html'
        ↓
CSS is loaded from 'static/css/main.css'
        ↓
Bootstrap styles the UI
        ↓
Browser shows the final webpage.
```

### Basic understanding

```
'layout.html' → website skeleton
'home.html'   → page content
'static/'     → styling + assets
FastAPI       → server connecting everything
```

-------

### Path parameters — validation & error handling

