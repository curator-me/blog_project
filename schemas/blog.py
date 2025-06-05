from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from .comment import CommentOut

class BlogIn(BaseModel):
    title: str
    body: str

class BlogOut(BaseModel):
    id: int
    title: str
    body: str
    time_created: datetime
    time_updated: datetime 
    likes: int
    comments: List[CommentOut]

    class Config:
        orm_mode = True

class BlogInDB(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
