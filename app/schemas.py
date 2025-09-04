from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint

class PostBase(BaseModel):
    title: str
    content: str 
    published: bool = True
    #rating: Optional[int] = None

class PostCreate(PostBase):
    pass


class UserConfirmation(BaseModel):
    email: EmailStr
    id: int
    createdat: datetime

    #Need to add this to be able to interpret ORM returns that are not dicts
    class Config:
        from_attributes = True


class Post(PostBase):
    id: int
    createdat: datetime
    user_id: int
    user: UserConfirmation

    class Config:
        #Need to add this to be able to interpret ORM returns that are not dicts
        from_attributes = True

        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    #Need to add this to be able to interpret ORM returns that are not dicts
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None

class Vote(BaseModel):
    post_id: int
    dir: int 

class PostOut(BaseModel):
    Post: Post  # Assuming Post is already defined
    Votes: int

    class Config:
        from_attributes = True


class Device(BaseModel):
    device_id: int

