from datetime import datetime
from typing import Any
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column
from enum import Enum


class User(SQLModel, table=True):
    '''
    Foundational User Model information
    End point for initiating DB model creation
    '''
    id:int | None=Field(default=None, primary_key=True)
    email:str = Field(unique=True, index=True, nullable=False)
    password:str = Field(nullable=False)
    role:str = Field(nullable=False)
