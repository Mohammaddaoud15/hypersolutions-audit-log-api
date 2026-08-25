from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import User
from app.schemas import Token, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):  # noqa: B008
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise BadRequestException(detail="Username already registered")

    hashed_pw = hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),  # noqa: B008
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )

    return {"access_token": access_token, "token_type": "bearer"}
