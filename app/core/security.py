from datetime import UTC, datetime, timedelta

import bcrypt
from jose import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt
