# importing modules
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# database connection url
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

# creating a connection to the database
engine = create_engine(
    url = SQLALCHEMY_DATABASE_URL,
    connect_args = {"check_same_thread": False}
)

# creating a session — each request gets it own session
SessionLocal = sessionmaker(
    autoflush = False,
    autocommit = False,
    bind = engine
)

# 
class Base(DeclarativeBase):
    pass

# function to provide a session to our routes
def get_db():
    with SessionLocal() as db:
        yield db
