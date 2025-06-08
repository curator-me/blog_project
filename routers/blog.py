from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..schemas.blog import BlogIn, BlogOut, BlogInDB
from ..schemas.comment import CommentOut
from ..schemas.like import Like
from ..schemas.catagory import Catagory
from ..database import get_db
from .. import models
from ..jwt_token import get_current_user

router = APIRouter(
    prefix='/blog',
    tags=['blog']
)

@router.get('/', response_model=BlogOut)
def get_blog(id: int = Query(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="blog not found")
    if blog.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='you cannot access this content')
    
    return blog


@router.get('/all', response_model=List[BlogOut])
def get_all_blogs(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # if not admin: raise exception
    blogs = db.query(models.Blog).all()
    return blogs



@router.get('/catagory', response_model=List[BlogOut])
def get_blogs_by_catagory(id: int = Query(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.catagory_id == id)

    return blog.all()

    
@router.post('/create', status_code=status.HTTP_201_CREATED)
def create_blog(request: BlogIn,new_catagory: Catagory, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    blog = models.Blog(
        title = request.title,
        body = request.body,
        author_id = current_user.id,
        # catagory_id = request.catagory_id,
    )

    id = db.query(models.Catagory).filter(models.Catagory.id == request.catagory_id).first()
    if id:    
        blog.catagory_id = request.catagory_id
    else:
        catagory = models.Catagory(name = new_catagory.name)
        db.add(catagory)
        db.commit()
        db.refresh(catagory)

        blog.catagory_id = catagory.id
        

    db.add(blog)
    db.commit()
    db.refresh(blog)

    return {'info': 'blog created successfully'}

@router.put('/{id}/update', status_code=status.HTTP_200_OK)
def update_blog(id: int, request: BlogInDB, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="blog not found")
    if blog.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="you can't change the content")
    
    if request.title != None:
        blog.title = request.title
    if request.body != None:
        blog.body = request.body

    db.commit()
    db.refresh(blog)
    return {'info': 'updated succesfully'}

@router.delete('/{id}/delete', status_code=status.HTTP_200_OK)
def delete_blog(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)

    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="blog not found")
    if blog.first().author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='you cannot delete this content')
    
    blog.delete(synchronize_session=False)
    db.commit()
    return {'info': 'deleted'}


@router.get('/{id}/comments', response_model=List[CommentOut])
def get_comments(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    comments = db.query(models.Comment).filter(models.Comment.blog_id == id)

    return comments.all()

@router.get('/{id}/likes', response_model=List[Like])
def get_likes(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    likes = db.query(models.Like).filter(models.Like.blog_id == id)

    return likes.all()