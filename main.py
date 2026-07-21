# importing the required modules
from contextlib import asynccontextmanager
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, status, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
# from fastapi.responses import JSONResponse
# from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Annotated

# importing local modules from other files
from schemas import PostCreate, PostResponse, PostUpdate, UserCreate, UserResponse, UserUpdate
import models
from database import Base, engine, get_db

# creating database table
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    # shutdown
    await engine.dispose()

# initializing the app
app = FastAPI(lifespan = lifespan)

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
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Post).options(selectinload(models.Post.author))
    )
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
async def post_page(
    request: Request,
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id)
    )
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
async def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )
    
    result = await db.execute(
        select(models.Post).options(selectinload(models.Post.author)).where(models.Post.user_id == user_id)
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
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    # for username
    result = await db.execute(
        select(models.User).where(models.User.username == user.username)
    )

    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Username already exists"
        )
    
    # for email
    result = await db.execute(
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
    await db.commit()           # saves and commits the changes
    await db.refresh(new_user)  # refresh the database

    return new_user

# API FOR GETTING USER'S INFO BY USER ID
@app.get("/api/users/{user_id}", response_model = UserResponse)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
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
async def get_user_posts(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )

    result = await db.execute(
        select(models.Post).options(selectinload(models.Post.author)).where(models.Post.user_id == user_id)
    )

    posts = result.scalars().all()
    return posts

@app.patch(path = "/api/users/{user_id}", response_model = UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )
    
    if user_update.username is not None and user_update.username != user.username:
        result = await db.execute(
            select(models.User).where(models.User.username == user_update.username)
        )
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Username already exists"
            )
    
    if user_update.email is not None and user_update != user.email:
        result = await db.execute(
            select(models.User).where(models.User.email == user_update.email)
        )
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Email already exists"
            )
    
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.image_file is not None:
        user.image_file = user_update.image_file

    await db.commit()
    await db.refresh(user)
    return user

# -------- POST API PAGE --------
# returns single post, as response
@app.get("/api/posts", response_model = list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts

# ------ FOR GETTING INDIVIDUAL POST PAGE ------
@app.get("/api/posts/{post_id}", response_model = PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
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
async def update_post_full(
    post_id: int,
    post_data: PostCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Post not found"
        )
    if post_data.user_id != post.user_id:
        result = await db.execute(select(models.User).where(models.User.id == post_data.user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id

    await db.commit()
    await db.refresh(post, attribute_names = ["author"])
    return post

# ------ REQUEST VALIDATION ERROR HANDLING ------
# this handles the wrong input type, missing data, validation failures
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)

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

# --------- PARTIAL POST UPDATE ---------
@app.patch(
    path = "/api/posts/{post_id}",
    response_model = PostResponse
)
async def update_post_partial(
    post_id: int,
    post_data: PostUpdate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Post not found"
        )
    
    update_data = post_data.model_dump(exclude_unset = True)
    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post, attribute_names = ["author"])
    return post

@app.delete(path = "/api/posts/{post_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Post not found"
        )
    
    db.delete(post)
    await db.commit()

# ------ GENERAL ERROR HANDLING ------
# this handles the page not found exceptions
@app.exception_handler(StarletteHTTPException)
async def general_exception_handler(request: Request, exception: StarletteHTTPException):
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)
    
    message = (
        exception.detail
        if exception.detail
        else "An error occured. Please check your request and try again."
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
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == post.user_id))
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
    await db.commit()
    await db.refresh(new_post, attribute_names = ["author"])

    return new_post

# ---------- DELETE THE USER ----------
@app.delete("/api/users/{user_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    statement = select(models.User).where(models.User.id == user_id)
    user = await db.execute(statement).scalars().first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"User with user ID {user_id} not found!"
        )
    
    await db.delete(user)
    await db.commit()

