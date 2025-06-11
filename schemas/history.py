from datetime import datetime
from pydantic import BaseModel

class HistoryOut(BaseModel):

    blog_id : int
    blog_title : str
    viewed_at : datetime