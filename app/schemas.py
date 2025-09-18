from pydantic import BaseModel, EmailStr
from datetime import datetime

# for register requests
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# showing a user
class UserRead(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    # auto convert from SQLAlchemy object to schema
    class Config:
        from_attributes = True  

# for login responses
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CategoryCreate(BaseModel):
    name: str

class CategoryRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

