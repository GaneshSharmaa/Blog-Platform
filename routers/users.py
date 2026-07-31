# importing required modules
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from PIL import UnidentifiedImageError
from starlette.concurrency import run_in_threadpool

# importing local modules
import models
from database import get_db
from schemas import PostResponse, UserCreate, UserPrivate, UserPublic, UserUpdate, Token
from auth import CurrentUser, create_access_token, hash_password, verify_password
from config import settings
from image_utils import delete_profile_image, process_profile_image

router = APIRouter()

# --------- CREATING A NEW POST ---------
@router.post(
    path = "",
    response_model = UserPrivate,
    status_code = status.HTTP_201_CREATED
)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # for username
    result = await db.execute(
        select(models.User).where(func.lower(models.User.username) == user.username.lower())
    )

    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Username already exists"
        )
    
    # for email
    result = await db.execute(
        select(models.User).where(func.lower(models.User.email) == user.email.lower())
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
        email = user.email.lower(),
        hashed_password = hash_password(user.password)
    )

    db.add(new_user)      # stages the changes
    await db.commit()           # saves and commits the changes
    await db.refresh(new_user)  # refresh the database

    return new_user

@router.post("/token", response_model = Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.User).where(
            func.lower(models.User.email) == form_data.username.lower()
        )
    )

    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect email or password"
        )

    access_token_expires = timedelta(minutes = settings.access_token_expire_min)

    access_token = create_access_token(
        data = {"sub": str(user.id)},
        expires_delta = access_token_expires
    )

    return Token(
        access_token = access_token,
        token_type = "bearer"
    )

@router.get("/me", response_model = UserPrivate)
async def get_current_user(current_user: CurrentUser):
    return current_user

# ------ GETTING USER INFORMATION BY USER ID ------
@router.get("/{user_id}", response_model = UserPublic)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
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

# --- GETTING ALL POSTS BY A USER BY USING USER ID ---
@router.get(
    path = "/{user_id}/posts",
    response_model = list[PostResponse]
)
async def get_user_posts(
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
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.date_posted.desc())
    )

    posts = result.scalars().all()
    return posts

# ------ PARTIALLY UPDATING USER INFORMATION ------
@router.patch(path = "/{user_id}", response_model = UserPrivate)
async def update_user(user_id: int, user_update: UserUpdate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if user_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Not authorized to update this user"
        )

    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )
    
    if user_update.username is not None and user_update.username.lower() != user.username.lower():
        result = await db.execute(
            select(models.User).where(func.lower(models.User.username) == user_update.username.lower())
        )
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Username already exists"
            )
    
    if user_update.email is not None and user_update.email.lower() != user.email.lower():
        result = await db.execute(
            select(models.User).where(func.lower(models.User.email) == user_update.email.lower())
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
        user.email = user_update.email.lower()

    await db.commit()
    await db.refresh(user)
    return user

# --------- DELETING A USER BY USER ID ---------
@router.delete("/{user_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if user_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Not authorized to update this post"
        )

    statement = select(models.User).where(models.User.id == user_id)
    user = await db.execute(statement).scalars().first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"User with user ID {user_id} not found!"
        )
    
    await db.delete(user)
    await db.commit()

@router.patch("/{user_id}/picture", response_model = UserPrivate)
async def upload_profile_picture(
    user_id: int,
    file: UploadFile,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Not authorized to update this user's picture"
        )

    content = await file.read()

    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"File too large. Maximum size is {settings.max_upload_size_bytes // (1024 * 1024)} MB"
        )

    try:
        new_filename = await run_in_threadpool(process_profile_image, content)
    except UnidentifiedImageError as err:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Invalid image file. Please upload a valid image (JPEG, PNG, GIF, WebP)."
        ) from err

    old_filename = current_user.image_file

    current_user.image_file = new_filename
    await db.commit()
    await db.refresh(current_user)

    if old_filename:
        delete_profile_image(old_filename)

    return current_user

@router.delete("/{user_id}/picture", response_model = UserPrivate)
async def delete_user_picture(
    user_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Not athorized to delete this user's picture."
        )

    old_filename = current_user.image_file

    if old_filename is None:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "No profile picture to delete"
        )

    current_user.image_file = None
    await db.commit()
    await db.refresh(current_user)

    delete_profile_image(old_filename)
    return current_user

@router.delete("/{user_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Not authorized to delete this user"
        )

    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )

    old_filename = user.image_file

    await db.delete(user)
    await db.commit()

    if old_filename:
        delete_profile_image(old_filename)

