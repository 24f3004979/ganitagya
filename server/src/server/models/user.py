from datetime import datetime
from typing import Any
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column

# Making user model working through data base

class User(SQLModel):
    '''
    Simple user model object
    functions
        - Uses verification function for login functionality with password
        - Editing endpoint about user details
        - Simple update wrappers
    '''

