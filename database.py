# importing modules
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import settings

# creating a connection to the database
engine = create_async_engine(
    settings.database_url
)

# creating a session — each request gets it own session
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_ = AsyncSession,
    expire_on_commit = False
)

# 
class Base(DeclarativeBase):
    pass

# function to provide a session to our routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
