from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from ..jwt_token import get_current_user
from ..database import get_db
from .. import models


router = APIRouter(
    prefix='/tag',
    tags=['tags']
)


@router.post('/add')
def add_tag(tag_name: str, db: Session = Depends(get_db),  current_user: models.User = Depends(get_current_user)):
    tag_name = tag_name.strip().lower()

    tag = db.query(models.Tag).filter(models.Tag.name == tag_name)

    if tag.first():
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Already exist!")
    
    tag = models.Tag(name = tag_name)

    db.add(tag)
    db.commit()
    db.refresh(tag)
    
    return {'info': 'tag added'}



@router.delete('/delete')
def delete_tag(tag_name: str, db: Session = Depends(get_db),  current_user: models.User = Depends(get_current_user)):
    tag = db.query(models.Tag).filter(models.Tag.name == tag_name)

    if not tag.first():
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail='no tag found')
    
    tag.delete(synchronize_session=False)
    db.commit()

    return {'info': 'deleted'}