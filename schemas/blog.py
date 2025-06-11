from typing import List, Optional
from pydantic import BaseModel, field_validator
from datetime import datetime

class BlogIn(BaseModel):
    title: str
    body: str
    category_name: Optional[str] = None
    tags:Optional[List[str]] = None

    @field_validator("tags")
    @classmethod
    def check_valid_tag(cls, v):
        if v is not None and len(v) > 5:
            raise ValueError("Maximum 5 tags allowed")
        return v
    

class BlogOut(BaseModel):
    id: int
    title: str
    time_created: datetime
    time_updated: datetime 
    view_count: int
    likes_count: int
    comments_count: int
    category_name: Optional[str] = None
    tags:Optional[List[str]] = None

    class Config:
        orm_mode = True

class BlogInDB(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    category_name: Optional[str] = None
    tags:Optional[List[str]] = None
