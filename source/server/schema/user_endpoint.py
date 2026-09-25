from pydantic import BaseModel, EmailStr

'''
Using one universal schema for data flow for registration and login both interfaces
'''

class Input(BaseModel):
    '''Input Base Model
    Used for
    1. Authentication
    2. Registration
    '''
    email: EmailStr
    password: str
