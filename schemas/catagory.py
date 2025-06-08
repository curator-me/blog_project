from pydantic import BaseModel
from typing import Optional

class Catagory(BaseModel):
    name: Optional[str] = None

    