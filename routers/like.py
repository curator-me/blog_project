from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from ..jwt_token import get_current_user
from ..database import get_db
from .. import models


router = APIRouter(
    prefix='/like',
    tags=['likes']
)

@router.post('/{blog_id}/like')
def add_like(id: int, db: Session = Depends(get_db),  current_user: models.User = Depends(get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail='blog not found')

    like = db.query(models.Like).filter(models.Like.blog_id == blog.id).first()

    if like:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='already liked')

    like = models.Like()
    like.blog_id = blog.id
    like.reactor_id = current_user.id 

    db.add(like)
    db.commit()
    db.refresh(like)
    
    return {'info': 'liked'}


@router.post('/{blog_id}/unlike')
def unlike(id: int, db: Session = Depends(get_db),  current_user: models.User = Depends(get_current_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail='blog not found')

    like = db.query(models.Like).filter(models.Like.blog_id == blog.id).first()

    if not like:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='already liked')
    if like.reactor_id is not current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    db.delete(like)
    db.commit()
    
    return {'info': 'unliked'}