# importing the required modules
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
# from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# initializing the app
app = FastAPI()

# static folder access to the FastAPI
app.mount("/static", StaticFiles(directory = "static"), name = "static")

# creating a HTML template
templates = Jinja2Templates(directory = "./templates")

# posts data for the app (later will be shifted to database)
posts: list[dict] = [
    {
        "id": 1,
        "author": "Ganesh Sharma",
        "title": "Getting started with AI/ML",
        "content": "Stay tuned!",
        "date_posted": "May 27, 2026",
        "profile_pic": "/static/profile-picture/you.jpg"
    },
    {
        "id": 2,
        "author": "John Doe",
        "title": "Python increase day-by-day",
        "content": "Python is a great language.",
        "date_posted": "May 27, 2026",
        "profile_pic": "/static/profile-picture/you.jpg"
    },
    {
        "id": 3,
        "author": "Ben 10",
        "title": "Increasing Global Warming — El Nino",
        "content": "You might have noticed the heat now in summers.",
        "date_posted": "May 24, 2026",
        "profile_pic": "/static/profile-picture/you.jpg"
    },
    {
        "id": 4,
        "author": "Mary Jane",
        "title": "I love SpiderMan",
        "content": "Spiddy, you're a hero! I swear to God, for real!",
        "date_posted": "May 25, 2026",
        "profile_pic": "/static/profile-picture/you.jpg"
    },
    {
        "id": 5,
        "author": "Narendra Modi",
        "title": "India 2047 — A vision",
        "content": "The future I see for this country, I think is achievable by 2047.",
        "date_posted": "April 30, 2026",
        "profile_pic": "/static/profile-picture/you.jpg"
    },
    {
        "id": 6,
        "author": "Will Hunting",
        "title": "For God sake, please stop living inside your head",
        "content": "Stop living inside your head, and it's not your fault for not knowing earlier that time could only teach you. Whatever happened, happened, now live and cherish the present, present is what only exists, so live it.",
        "date_posted": "May 25, 2026",
        "profile_pic": "/static/profile-picture/you.jpg"
    },
]

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

# -------- ALL POST API PAGE -------- 
@app.get("/api/posts")
def get_posts():
    return posts

# -------- POST API PAGE -------- 
@app.get("/api/posts/{post_id}")
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
