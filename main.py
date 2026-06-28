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
from schemas import PostCreate, PostResponse, UserCreate, UserResponse, PostUpdate
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
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request = request,
        name = "home.html",
        context = {
            "posts": posts,
            "title": "Home"
        }
    )

# -------- POST PAGE -------- 
@app.get("/posts/{post_id}", include_in_schema = False)
def post_page(
    request: Request,
    post_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request = request,
            name = "post.html",
            context = {
                "post": post,
                "title": title
            }
        )
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "Post not found"
    )

# ------------ USER POST PAGE ------------
@app.get(
    path = "/users/{user_id}/posts",
    include_in_schema = False,
    name = "user_posts"
)
def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )
    
    result = db.execute(
        select(models.Post).where(models.Post.user_id == user_id)
    )
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request = request,
        name = "user_posts.html",
        context = {
            "posts": posts,
            "user": user,
            "title": f"{user.username}'s Posts"
        }
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

# 
@app.get("/api/users/{user_id}", response_model = UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == user_id)
    )

    user = result.scalars().first()

    if user:
        return user
    
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "User not found"
    )

# -------- ALL POST API PAGE -------- 
# returns list of posts, as response
@app.get(
    path = "/api/users/{user_id}/posts",
    response_model = list[PostResponse]
)
def get_user_posts(
    user_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(
        select(models.User).where(models.User.id == user_id)
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )

    result = db.execute(
        select(models.Post).where(models.Post.user_id == user_id)
    )

    posts = result.scalars().all()
    return posts

# -------- POST API PAGE --------
# returns single post, as response
@app.get("/api/posts", response_model = list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts

# ------ FOR GETTING INDIVIDUAL POST PAGE ------
@app.get("/api/posts/{post_id}", response_model = PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "Post not found"
    )

# ----------- UPDATING THE POST -----------
@app.put(
    path = "/api/posts/{post_id}",
    response_model = PostResponse
)
def update_post_full(
    post_id: int,
    post_data: PostCreate,
    db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Post not found"
        )
    if post_data.user_id != post.user_id:
        result = db.execute(select(models.User).where(models.User.id == post_data.user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id

    db.commit()
    db.refresh(post)
    return post

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
    path = "/api/posts",
    response_model = PostResponse,
    status_code = status.HTTP_201_CREATED
)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )
    
    new_post = models.Post(
        title = post.title,
        content = post.content,
        user_id = post.user_id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

