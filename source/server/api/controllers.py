from server.service.user import register_user
from server.dev_log import *
from fastapi.responses import JSONResponse
# from fastapi import status # Status code response to front end endpoint
from server.exceptions import UserExists
from server.schema.user_endpoint import UserRegisterInput

'''
Controller Units
Working as simple data processor layer between services and working end point api to handle responses generation

Final service layer wrapper with response grids
used with routes directly for serving through front end part of the application
'''

# Simple registration end point
def Registration(information:UserRegisterInput):
    log.info(f'Registration Initiated : {information}')
    try:
        # converting information to dictionary format
        info_load = {
                "email": information.email,
                "password": information.password,
                "role" : "student"
                }
        if register_user(info_load):
            return {"message" : "Registration completed", "status": 200}
    except UserExists as e:
        return {"message" : "Registration Failed", "status" : 404}

