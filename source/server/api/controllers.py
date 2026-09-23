from server.service.user import register_user
from server.dev_log import *
from fastapi.responses import JSONResponse
from fastapi import status

'''
Controller Units
Working as simple data processor layer between services and working end point api to handle responses generation

Final service layer wrapper with response grids
used with routes directly for serving through front end part of the application
'''

# Simple registration end point
def Registration(information):
    log.info(f'Registration Initiated : {information}')
    try:
        if register_user(information):
            return {"message" : "Registration completed", "status": 200}
    except UserExists as e:
        return {"message" : "Registration Failed", "status" : 404}

