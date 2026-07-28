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
import models
from database import Base, engine, get_db
from routers import posts, users

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

# creating users and posts routes
app.include_router(users.router, prefix = "/api/users", tags = ["users"])
app.include_router(posts.router, prefix = "/api/posts", tags = ["posts"])

# -------- HOME PAGE -------- 
@app.get("/", include_in_schema = False, name = "home")
@app.get("/posts", include_in_schema = False, name = "posts")
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
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
    db: AsyncSession = Depends(get_db)
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
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.User)
        .where(models.User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )
    
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author)).where(models.Post.user_id == user_id)
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

# ----------- LOGIN ROUTE -----------
@app.get("/login", include_in_schema = False)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "login.html",
        context = {
            "title": "Login"
        }
    )

# ----------- REGISTER ROUTE -----------
@app.get("/register", include_in_schema = False)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "register.html",
        context = {
            "title": "Register"
        }
    )

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

