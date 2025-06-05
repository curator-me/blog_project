from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..schemas.blog import BlogIn, BlogOut, BlogInDB
from ..schemas.comment import CommentOut
from ..schemas.like import LikeOut
from ..database import get_db
from ..models import Blog, User, Comment, Like
from ..jwt_token import get_current_user

router = APIRouter(
    prefix='/blog',
    tags=['blog']
)

@router.get('/all', response_model=List[BlogOut])
def get_all_blogs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # if not admin: raise exception
    blogs = db.query(Blog).all()
    return {'info': blogs}

@router.get('/{id}', response_model=BlogOut)
def get_blog(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog = db.query(Blog).filter(Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="blog not found")
    if blog.author_id is not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='you cannot access this content')
    
    return {'info': blog}

@router.get('/{author_id}', response_model=List[BlogOut])
def get_blogs(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if id is not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='you cannot access this content')
    
    blogs = db.query(Blog).filter(Blog.author_id == id)

    if not blogs.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="blog not found")
    
    return {'info': blogs}


    
@router.post('/create', status_code=status.HTTP_201_CREATED)
def create_blog(request: BlogIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog = Blog(
        title = request.title,
        body = request.body,
        authro_id = current_user.id,
    )

    db.add(blog)
    db.commit()
    db.refresh(blog)

    return {'info': 'blog created successfully'}

@router.put('/{id}/update', status_code=status.HTTP_200_OK)
def update_blog(id: int, request: BlogInDB, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog = db.query(Blog).filter(Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="blog not found")
    if blog.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="you can't change the content")
    
    if request.title is not None:
        blog.title = request.title
    if request.body is not None:
        blog.body = request.body

    db.commit()
    return {'info': 'updated succesfully'}

@router.delete('/{id}/delete', status_code=status.HTTP_200_OK)
def delete_blog(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog = db.query(Blog).filter(Blog.id == id)

    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="blog not found")
    if blog.first().author_id is not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='you cannot delete this content')
    
    blog.delete(synchronize_session=False)
    db.commit()
    return {'info': 'deleted'}


@router.get('/{id}/comments', response_model=List[CommentOut])
def get_comments(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comments = db.query(Comment).filter(Comment.blog_id == id).all()

    return comments.sort(reverse=True)

@router.get('/{id}/likes', response_model=LikeOut)
def get_likes(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    likes = db.query(Like).filter(Like.blog_id == id).all()

    if likes.__len__() == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No likes found")
    return likes.sort(reverse=True)