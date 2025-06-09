from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..schemas.category import Category
from ..database import get_db
from .. import models
from ..jwt_token import get_current_user

router = APIRouter(
    prefix='/category',
    tags=['category'],
)

@router.post('/create')
def create_category(request: Category ,db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    search = db.query(models.Category).filter(models.Category.name == request.name).first()

    if search:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Category already exist')
    
    category = models.Category(name = request.name)

    db.add(category)
    db.commit()
    db.refresh(category)

    return {'info': 'created'}

@router.delete('/{id}/delete', status_code=status.HTTP_200_OK)
def delete_category(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    category = db.query(models.Category).filter(models.Category.id == id)

    if not category.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="category not found")
    
    category.delete(synchronize_session=False)
    db.commit()
    return {'info': 'deleted'}
