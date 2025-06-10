from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy import func
from ..jwt_token import get_current_user
from ..schemas.blog import BlogOut
from ..schemas.comment import CommentOut
from ..schemas.like import Like
from ..schemas.user import UserOut, UserInDB
from ..database import get_db
from sqlalchemy.orm import Session, joinedload
from .. import models
import random

router = APIRouter(prefix="/user", tags=["user"])

@router.get('/', response_model=UserOut)
def get_user(id: int = Query(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user

@router.get('/all', response_model=List[UserOut])
def get_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # if not admin: raise exception
    users = db.query(models.User).all()
    return users


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

    if id != current_user.id:       # or not admin
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You cannot perform this action')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )

    db.delete(user)
    db.commit()

    return {'info': 'deleted'}

@router.get('/my-likes', response_model=List[Like] ,status_code=status.HTTP_200_OK)
def my_likes(db: Session = Depends(get_db),  current_user: models.User = Depends(get_current_user)):
    likes = db.query(models.Like).filter(models.Like.reactor_id == current_user.id)

    return likes.all()

@router.get('/my-comments', response_model=List[CommentOut] ,status_code=status.HTTP_200_OK)
def my_comments(db: Session = Depends(get_db),  current_user: models.User = Depends(get_current_user)):
    comments = db.query(models.Comment).filter(models.Comment.commenter_id == current_user.id)

    return comments.all()

@router.get('/my-blogs' ,response_model=List[BlogOut])
def my_blogs(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    blogs = db.query(models.Blog).filter(models.Blog.author_id == current_user.id).options(
        joinedload(models.Blog.category),
        joinedload(models.Blog.tags),
    )

    return blogs.all()

@router.get('/my-favorites', response_model=List[BlogOut])
def get_favorite_blogs(skip: int = 0, limit: int = 10 ,db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db,query(models.Blog)

    favorites = db.query(models.Blog).join(
        models.favorite_blog_table,
        models.Blog.id == models.favorite_blog_table.c.blog_id,
    ).filter(models.favourite_blog_table.c.user_id == current_user.id).options(
            joinedload(models.Blog.category),
            joinedload(models.Blog.tags),
    ).order_by(models.Blog.time_created.desc()).offset(skip).limit(limit).all()

    return favorites


@router.post('/favorite/add/{id}', status_code=status.HTTP_200_OK)
def add_to_favorite_blog(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="blog not found")
    
    if blog.is_favorited(current_user.id, blog.id, db):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Already exist')
    
    current_user.favourite_blogs.append(blog)
    blog.favourite_count += 1

    db.commit()

    return {'info': 'blog added to favorite!!'}



@router.delete('/favorite/remove/{id}', status_code=status.HTTP_200_OK)
def remove_from_favorite_blog(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not models.Blog.is_favorited(current_user.id, id, db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Blog not found in favorites')

    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )

    db.execute(
        models.favourite_blog_table.delete().where(
            models.favourite_blog_table.c.user_id == current_user.id,
            models.favourite_blog_table.c.blog_id == id,
        )
    )

    blog.favourite_count -= 1

    if random.random() < 0.01:  # verify fovorite_count ( 1% chance )
        actual_count = (
            db.query(func.count(models.favorite_blog_table.c.blog_id))
            .filter(models.favorite_blog_table.c.blog_id == id)
            .scalar()
        )

        if blog.favourite_count != actual_count:
            blog.favourite_count = actual_count

    return {'info': 'Removed form favorite!!'}
