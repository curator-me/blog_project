from typing import Optional
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    username: str
    password: str

class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserOut(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    firstname: str
    lastname: str
    


class UserInDB(BaseModel):
    email: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    location: Optional[str] = None

    # this Optional let us to send data for the desire feild only #