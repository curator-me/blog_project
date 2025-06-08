from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..schemas.catagory import Catagory
from ..database import get_db
from .. import models
from ..jwt_token import get_current_user

router = APIRouter(
    prefix='/catagory',
    tags=['catagory'],
)

@router.post('/create')
def create_catagory(request: Catagory ,db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    search = db.query(models.Catagory).filter(models.Catagory.name == request.name).first()

    if search:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Catagory already exist')
    
    catagory = models.Catagory(name = request.name)

    db.add(catagory)
    db.commit()
    db.refresh(catagory)

    return {'info': 'created'}

@router.delete('/{id}/delete', status_code=status.HTTP_200_OK)
def delete_catagory(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    catagory = db.query(models.Catagory).filter(models.Catagory.id == id)

    if not catagory.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="catagory not found")
    
    catagory.delete(synchronize_session=False)
    db.commit()
    return {'info': 'deleted'}
