from pydantic import BaseModel, EmailStr

class UserRegisterInput(BaseModel):
    '''Defaulting for making only student from registration routes'''
    email: EmailStr
    password: str
