from typing import List
from pydantic import BaseModel
from datetime import datetime

class Like(BaseModel):
    reactor_id : int
    blog_id : int
    time_liked : datetime

