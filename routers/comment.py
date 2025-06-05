from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..jwt_token import get_current_user
from .. import models
from ..schemas.comment import CommentIn, CommentInDB
from ..schemas.blog import BlogOut


router = APIRouter(
    prefix='/comments',
    tags=['comments']
)

@router.post('/{blog_id}/add-comment')
def add_comment(blog_id: int, request: CommentIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    comment = models.Comment()
    comment.blog_id = blog_id
    comment.commenter_id = current_user.id
    comment.body = CommentIn

    db.add(comment)
    db.commit()
    db.refresh(comment)

@router.put('/{id}')
def update_comment(id: int, request: CommentInDB, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    comment = db.query(models.Comment).filter(models.Comment.id == id).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no comment found")
    if comment.commenter_id is not current_user.id:
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, detail='You cannot perform this action')
    
    comment.body = request.body

    db.commit()
    db.refresh(comment)

    return {'info': 'updated'}

@router.delete('/{id}/delete')
def delete_comment(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    comment = db.query(models.Comment).filter(models.Comment.id == id).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no comment found")
    if comment.commenter_id is not current_user.id:
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, detail='You cannot perform this action')
    
    db.delete(comment)
    db.commit()

    return {'info': 'deleted'}

@router.get('/{comment_id}/blog', response_model=BlogOut)
def get_blog(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    comment = db.query(models.Comment).filter(models.Comment.id == id).first()
    blog = db.query(models.Blog).filter(models.Blog.id == comment.blog_id).first()

    if (not comment) or (not blog):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='nothing found')
    
    return blog