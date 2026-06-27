# importing the required modules
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, status, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
# from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Annotated

# importing local modules from other files
from schemas import PostCreate, PostResponse, UserCreate, UserResponse
import models
from database import Base, engine, get_db

# creating database table
Base.metadata.create_all(bind = engine)

# initializing the app
app = FastAPI()

# static folder access to the FastAPI
app.mount(
    path = "/static",
    app = StaticFiles(directory = "static"),
    name = "static"
)
app.mount(
    path = "/media",
    app = StaticFiles(directory = "media"),
    name = "media"
)

# creating a HTML template
templates = Jinja2Templates(directory = "./templates")

# -------- HOME PAGE -------- 
@app.get("/", include_in_schema = False, name = "home")
@app.get("/posts", include_in_schema = False, name = "posts")
def home(request: Request):
    # return {"message": "Hello World!"}
    return templates.TemplateResponse(
        request = request,
        name = "home.html",
        context = {
            "posts": posts,
            # "title": "FastAPI Blog",  # just commented out
            "limit": 5,
            "has_more": True
        }
    )

# -------- POST PAGE -------- 
@app.get("/posts/{post_id}", include_in_schema = False)
def post_page(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return templates.TemplateResponse(
                request = request,
                name = "post.html",
                context = {
                    "post": post,
                    "title": post["title"][:50],
                }
            )
    return templates.TemplateResponse(
        request = request,
        name = "error.html",
        context = {
            "request": request,
            "error_code": 404,
            "title": "Post Not Found",
            "error_message":
                "This post does not exist."
        },
        status_code = 404
    )

# -------------- FOR USERS --------------
@app.post(
    path = "/api/users",
    response_model = UserResponse,
    status_code = status.HTTP_201_CREATED
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    # for username
    result = db.execute(
        select(models.User).where(models.User.username == user.username)
    )

    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Username already exists"
        )
    
    # for email
    result = db.execute(
        select(models.User).where(models.User.email == user.email)
    )

    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Email already exists"
        )
    
    # for new user, username and email both doesn't already exists
    new_user = models.User(
        username = user.username,
        email = user.email
    )

    db.add(new_user)      # stages the changes
    db.commit()           # saves and commits the changes
    db.refresh(new_user)  # refresh the database

    return new_user

# -------- ALL POST API PAGE -------- 
# returns list of posts, as response
@app.get("/api/posts", response_model = list[PostResponse])
def get_posts():
    return posts

# -------- POST API PAGE --------
# returns single post, as response
@app.get("/api/posts/{post_id}", response_model = PostResponse)
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Post was not found!")

# ------ REQUEST VALIDATION ERROR HANDLING ------
# this handles the wrong input type, missing data, validation failures
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            content = {
                "detail": exception.errors()
            }
        )
    return templates.TemplateResponse(
        request = request,
        name = "error.html",
        context = {
            "error_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "error_title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "error_message": "Invalid request. Please check your input and try again."
        },
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    )

# ------ GENERAL ERROR HANDLING ------
# this handles the page not found exceptions
@app.exception_handler(StarletteHTTPException)
def general_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occured. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code = exception.status_code,
            content = {
                "detail": message
            }
        )
    
    return templates.TemplateResponse(
        request = request,
        name = "error.html",
        context = {
            "error_code": exception.status_code,
            "error_title": exception.status_code,
            "error_message": message
        },
        status_code = exception.status_code
    )

# --------- CREATE POST ---------
@app.post(
    "/api/posts",
    response_model = PostResponse,
    status_code = status.HTTP_201_CREATED
)
def create_post(post: PostCreate):
    new_id = max(p["id"] for p in posts) + 1 if posts else 1
    new_post = {
        "id": new_id,
        "author": post.author,
        "title": post.title,
        "content": post.content,
        "date_posted": "June 02, 2026"
    }
    posts.append(new_post)
    return new_post

