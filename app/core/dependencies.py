from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import CredentialsException
from app.database import get_db
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )

        username: str = payload.get("sub")
        if username is None:
            raise CredentialsException(detail="Token payload invalid")

    except JWTError:
        raise CredentialsException(detail="Could not validate credentials")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise CredentialsException(detail="User no longer exists")

    return user
