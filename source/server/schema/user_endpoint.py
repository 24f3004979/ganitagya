from pydantic import BaseModel

'''
Using one universal schema for data flow for registration and login both interfaces
Removed using username str explicitly into the main Input data structure

Swagger UI is broken with class not defined error
'''

class Input(BaseModel):
    '''Input Base Model
    Used for
    1. Authentication
    2. Registration
    '''
    username: str
    password: str

