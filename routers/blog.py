from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..schemas.blog import BlogIn, BlogOut, BlogInDB
from ..schemas.comment import CommentOut
from ..schemas.like import Like
from ..schemas.category import Category
from ..schemas.tag import Tag
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


@router.get('', response_model=List[BlogOut])
def search_blog(category: Optional[str] = Query(None), tag: Optional[str] = Query(None),
                db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(models.Blog)
    if category:
        query = query.join(Category).filter(models.Category.name == category)

    if tag:
        query = query.join(models.Blog.tags).filter(models.Tag.name == tag)

    return query.distinct().all()


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_blog(
    request: BlogIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)):

    category = db.query(models.Category).filter(models.Category.name == request.category_name).first()
    if not category:
        category = models.Category(name=request.category_name)
        db.add(category)
        db.commit()
        db.refresh(category)

    tag_objects = []
    if request.tags:
        for tag_name in request.tags:
            tag_name = tag_name.strip().lower()
            tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
            if not tag:
                tag = models.Tag(name=tag_name)
                db.add(tag)
            if tag not in tag_objects:
                tag_objects.append(tag)
    
    blog = models.Blog(
        title=request.title,
        body=request.body,
        author_id=current_user.id,
        category_id = category.id,
        tags=tag_objects,
    )
    
    db.add(blog)
    db.flush()

    return {"info": "Blog created successfully"}


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
    if not db.query(models.Blog).filter(models.Blog.id == id).first():
        raise HTTPException(status_code=404, detail="Blog not found")

    comments = db.query(models.Comment).filter(models.Comment.blog_id == id)

    return comments.all()

@router.get('/{id}/likes', response_model=List[Like])
def get_likes(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if not db.query(models.Blog).filter(models.Blog.id == id).first():
        raise HTTPException(status_code=404, detail="Blog not found")

    likes = db.query(models.Like).filter(models.Like.blog_id == id)

    return likes.all()

@router.get('/{id}/tags', response_model=List[Tag])
def get_tags(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="blog not found")
    
    return blog.tags
