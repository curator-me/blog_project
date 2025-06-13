from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from schemas.blog import BlogIn, BlogOut, BlogInDB
from schemas.comment import CommentOut
from schemas.like import Like
from schemas.category import Category
from schemas.tag import Tag
from database import get_db
import models
from jwt_token import get_current_user

router = APIRouter(
    prefix='/blog',
    tags=['blog']
)


# CRUD operations
@router.post('/create', status_code=status.HTTP_201_CREATED)
def create_blog(
    request: BlogIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)):

    category = db.query(models.Category).filter(models.Category.name == request.category_name).first()
    if not category:
        category = models.Category(name=request.category_name)
        db.add(category)
        db.flush()

    tag_objects = []
    if request.tags:
        for tag_name__ in request.tags:
            tag_name = tag_name__.strip().lower()
            if len(tag_name) == 0:
                continue
            tag_exist = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
            if not tag_exist:
                tag = models.Tag(name=tag_name)
                db.add(tag)
                db.flush()
            else:
                tag = tag_exist
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
    db.commit()

    return {"info": "Blog created successfully"}


@router.get('/get', response_model=BlogOut)
def get_blog(id: int = Query(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="blog not found")

    blog.view_count += 1
    history = db.query(models.History).filter(
        models.History.user_id == current_user.id,
        models.History.blog_id == blog.id,
    ).first()

    if history:
        history.viewed_at = func.now()
    else:
        history = models.History(
            user_id = current_user.id,
            blog_id = id
        )
        db.add(history)
        db.flush()

    
    db.commit()
    db.refresh(blog)

    return blog


@router.get('/all', response_model=List[BlogOut])
def get_all_blogs(skip: int = 0, limit: int = 10 ,db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # if not admin: raise exception
    blogs = db.query(models.Blog).offset(skip).limit(limit).all()
    return blogs


@router.put('/{id}/update', status_code=status.HTTP_200_OK)
def update_blog(id: int, request: BlogInDB, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="blog not found")
    if blog.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="you can't change the content")
    
    if request.title != None:
        blog.title = request.title
        blog.time_updated = func.now()
    if request.body != None:
        blog.body = request.body
        blog.time_updated = func.now()

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


# Search/filter operations
@router.get('/query', response_model=List[BlogOut])
def blog_query(category: Optional[str] = Query(None), tag: Optional[str] = Query(None),
                skip: int = 0, limit: int = 10,
                db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(models.Blog) 
    if category:
        query = query.join(models.Category).filter(models.Category.name == category).options(
            joinedload(models.Blog.category),
            joinedload(models.Blog.tags),
        )

    if tag:
        query = query.join(models.Blog.tags).filter(models.Tag.name == tag).options(
            joinedload(models.Blog.category),
            joinedload(models.Blog.tags),
        )

    return query.order_by(models.Blog.time_created.desc()).all()

@router.get('/search', response_model=List[BlogOut])
def search_blog(search_query: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if search_query.__len__() < 2:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='query is too short!!!')

    blog = db.query(models.Blog).join(models.Category).join(models.Tag).group_by(
        models.Blog.id, Category.name).filter(
            func.to_tsvector(
                'english',
                func.coalesce(models.Blog.title, '') + ' ' +
                func.coalesce(models.Blog.body, '') + ' ' +
                func.coalesce(models.Category.name, '') + ' ' + 
                func.coalesce(
                    func.aggregate_strings(Tag.name, ' '), ''
                )
            ).match(search_query)
        ).all()
           

    # blogs = db.query(models.Blog).filter(                     ## postgresql
    #         models.Blog.search_vector.match(search_query)
    #     ).all()
    

    return blog

# Relationship endpoints
@router.get('/{id}/comments', response_model=List[CommentOut])
def get_comments(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not db.query(db.query(models.Blog).filter(models.Blog.id == id).exists()).scalar():
        raise HTTPException(status_code=404, detail="Blog not found")

    return db.query(models.Comment).filter(models.Comment.blog_id == id).all()

@router.get('/{id}/likes', response_model=List[Like])
def get_likes(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if not db.query(models.Blog).filter(models.Blog.id == id).first():
        raise HTTPException(status_code=404, detail="Blog not found")

    return db.query(models.Like).filter(models.Like.blog_id == id).all()


@router.get('/{id}/tags', response_model=List[str])
def get_tags(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="blog not found")
    
    return [tag.name for tag in blog.tags]
