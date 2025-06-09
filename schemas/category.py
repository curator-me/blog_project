from pydantic import BaseModel
from typing import Optional

class Category(BaseModel):
    name: Optional[str] = None

    