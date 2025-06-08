from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..jwt_token import  getToken
from ..schemas import user, token
from ..database import get_db
from .. import models



router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pass(password: str):
    return pwd_context.hash(password)

def verify_pass(plain_pass, hash_pass):
    return pwd_context.verify(plain_pass, hash_pass)


@router.post("/create", status_code=status.HTTP_200_OK)
def register(request: user.UserIn, db: Session = Depends(get_db)):
    user = models.User(
        username=request.username,
        email=request.email,
        password=hash_pass(request.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"info": "user created successfully"}

@router.get('/login', response_model=token.Token)
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = (
        db.query(models.User).filter(models.User.username == request.username).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not verify_pass(request.password, user.password):
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )

    access_token = getToken(user.username)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
