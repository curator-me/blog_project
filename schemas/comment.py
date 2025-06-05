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
    comments : List[Comment]

class CommentInDB(BaseModel):
    body: str
