from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class UserBase(BaseModel):
    name: str
    age: int
    gender: str
    email: str
    city: str
    interests: str


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    interests: Optional[str] = None


class BulkUserCreate(BaseModel):
    users: List[UserCreate]


class User(UserBase):
    id: int

    # class Config:
    #     orm_mode = True
    model_config = ConfigDict(from_attributes=True)


class EmailRequest(BaseModel):
    email: str
