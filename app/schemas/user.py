from pydantic import BaseModel, EmailStr
import uuid

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"