from datetime import datetime
from typing import Any
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column

"""
Responsibility
+ User Information Manging unit 
+ Passoword
+ Name
+ Role

Implementation flow 
1. Implement simple user model
    
    Make user model work end to end from data base to front end
    User{
        id : Incremental Number
        name: Name
        Passowrd: hashed
        email : future mailing services requirements 
        role : student | Admin
    }

    Student(User){
        knowledge_graph = Meta information through the root graph of the system
            Student Mool graph Object -> Inherited version of the root knowledge graph
            with attached feat of mastry level of total 1st and 2nd - Based on siddhi module

            Student knowledge graph providing information about student current topics and ranks topics to test out
            Siddhi tests those listed and adjustes based on its internal mechanics with one topic hook
                Makes final report and talks to graph for new update
    }
"""


