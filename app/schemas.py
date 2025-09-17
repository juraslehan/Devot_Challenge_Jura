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

    class Config:
        from_attributes = True  # allows converting SQLAlchemy -> Pydantic

# for login responses
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
