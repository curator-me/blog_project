from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class BlogIn(BaseModel):
    title: str
    body: str
    catagory_id: int

class BlogOut(BaseModel):
    id: int
    title: str
    body: str
    time_created: datetime
    time_updated: datetime 
    likes_count: int
    comments_count: int

    class Config:
        orm_mode = True

class BlogInDB(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
