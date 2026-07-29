# importing the required modules
from datetime import UTC, datetime, timedelta
import jwt
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

# importing the local modules
from config import settings
import models
from database import get_db

# creating a password hashing object
password_hash = PasswordHash.recommended()

# creating a password bearer object
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/api/users/token")

# function to hash password
def hash_password(password: str) -> str:
    return password_hash.hash(password)

# function to verify the entered password
def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)

# function to create the access token for JWT authentication
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta is not None:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes = settings.access_token_expire_min)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm = settings.algorithm
    )

    return encoded_jwt

# function to verify the access token
def verify_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms = [settings.algorithm]
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")

# function for user lookup using the authenticated bearer tokens for authorization
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)]) -> models.User:
    user_id = verify_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired token",
            headers = {"WWW-Authenticate": "Bearer"}
        )

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired token",
            headers = {"WWW-Authenticate": "Bearer"}
        )

    user = await db.scalar(
        select(models.User).where(models.User.id == user_id_int)
    )

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "User not found",
            headers = {"WWW-Authenticate": "Bearer"}
        )

    return user

# simplifying the use of information extraction from the token
CurrentUser = Annotated[models.User, Depends(get_current_user)]

