from typing import Optional, Dict, Any
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON
from server.models.user import User 
from enum import Enum

class status(Enum):
    STARTED = 'started'
    LEARNING = 'learning'
    COMPLETED = 'completed'

class Student(SQLModel, table=True):
    '''
    Student Data Model
    Add new knowledge topic into graph
    Connected with user table
    '''
    student_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    knowledge_graph : Dict[str, str] = Field(sa_column=Column(JSON), default_factory=dict)
    user: Optional[User] = Relationship()
