from typing import List
from pydantic import BaseModel
from datetime import datetime

class Like(BaseModel):
    username : str
    blog_id : int
    date_liked : datetime

class LikeOut(BaseModel):
    likes : List[Like]