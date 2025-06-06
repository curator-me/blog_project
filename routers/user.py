from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from ..jwt_token import get_current_user
from ..schemas.blog import BlogOut
from ..schemas.comment import CommentOut
from ..schemas.like import Like
from ..schemas.user import UserOut, UserInDB
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models


router = APIRouter(prefix="/user", tags=["User"])

@router.get('/all', response_model=List[UserOut])
def get_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # if not admin: raise exception
    users = db.query(models.User).all()
    return users

@router.get('/my-likes', response_model=List[Like] ,status_code=status.HTTP_200_OK)
def my_likes(db: Session = Depends(get_db),  current_user: models.User = Depends(get_current_user)):
    likes = db.query(models.Like).filter(models.Like.reactor_id == current_user.id)

    return likes.all()

@router.get('/my-comment', response_model=List[CommentOut] ,status_code=status.HTTP_200_OK)
def my_comments(db: Session = Depends(get_db),  current_user: models.User = Depends(get_current_user)):
    comments = db.query(models.Comment).filter(models.Comment.commenter_id == current_user.id)

    return comments.all()

@router.get('/my-blogs' ,response_model=List[BlogOut])
def my_blogs(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    blogs = db.query(models.Blog).filter(models.Blog.author_id == current_user.id)

    return blogs.all()

@router.get('/{id}', response_model=UserOut)
def get_user(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/{id}/update", status_code=status.HTTP_200_OK)
def update_user(id: int,request: UserInDB, db: Session = Depends(get_db),  current_user: models.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if id is not current_user.id:       # or not admin
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You cannot perform this action')
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found",
        )

    if request.email is not None:
        user.email = request.email
    if request.firstname is not None:
        user.firstname = request.firstname
    if request.lastname is not None:
        user.lastname = request.lastname
    if request.location is not None:
        user.location = request.location

    db.commit()
    db.refresh(user)

    return {"info": "User updated successfully!"}


@router.delete("/{id}/delete", status_code=status.HTTP_200_OK)
def delete_user(id: int, db: Session = Depends(get_db),  current_user: models.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if id is not current_user.id:       # or not admin
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You cannot perform this action')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )

    db.delete(user)
    db.commit()

    return {'info': 'deleted'}