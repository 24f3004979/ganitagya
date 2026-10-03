from server.service.SiddhiManager import SiddhiUnit
from server.api.controllers import Registration 
from server.schema.user_endpoint import Input
from server.dev_log import *
from server.database import * 

Initiate_database()

unit = SiddhiUnit(1, 'Basic Arithmetic')
info =  Input(username='student@gmail.com', password='1234')
resp = Registration(info) # Student registered with id 1
log.info(f'Testing initiated with registration unit initiation sequence : {resp}')

# Initiate the student along with user registration flow

def test_generation():
    response = unit.generation(1)
    print(f"Generated response List : {response}")
    assert len(response) == 2

def test_evaluation():
    resp =  unit.evaluation([80,90])
    assert type(resp) == int
