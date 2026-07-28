# importing the required modules
from datetime import UTC, datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

# importing the local modules
from config import settings

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

