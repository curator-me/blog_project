from typing import List
from pydantic import BaseModel
from datetime import datetime


class Comment(BaseModel):
    id: int
    body: str
    time_created: datetime
    created_by: int
    
    class Config:
        orm_mode = True

class CommentIn(BaseModel):
    body: str

class CommentOut(BaseModel):
    id: int
    body: str
    time_commented: datetime
    commenter_id: int

    class Config:
        orm_mode = True


class CommentInDB(BaseModel):
    body: str
