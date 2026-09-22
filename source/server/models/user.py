from datetime import datetime
from typing import Any
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class User(SQLModel):
    '''
    Foundational User Model information
    End point for initiating DB model creation
    '''
    email:str = Field(unique=True, index=True, nullable=False)
    password:str = Field(nullable=False)
    role:UserRole = Field(nullable=False)

