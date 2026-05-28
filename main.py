# importing the required modules
from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# initializing the app
app = FastAPI()

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
    },
    {
        "id": 2,
        "author": "John Doe",
        "title": "Python increase day-by-day",
        "content": "Python is a great language.",
        "date_posted": "May 27, 2026",
    },
    {
        "id": 3,
        "author": "Ben 10",
        "title": "Increasing Global Warming — El Nino",
        "content": "You might have noticed the heat now in summers.",
        "date_posted": "May 24, 2026",
    },
    {
        "id": 4,
        "author": "Mary Jane",
        "title": "I love SpiderMan",
        "content": "Spiddy, you're a hero! I swear to God, for real!",
        "date_posted": "May 25, 2026",
    },
]

@app.get("/", include_in_schema = False)
@app.get("/posts", include_in_schema = False)
def home(request: Request):
    # return {"message": "Hello World!"}
    return templates.TemplateResponse(
        request = request,
        name = "home.html",
        context = {
            "posts": posts,
            "title": "Home",
            "limit": 5,
            "has_more": True
        }
    )

@app.get("/api/posts")
def get_posts():
    return posts
