from server.dev_log import *
from fastapi.responses import JSONResponse
# from fastapi import status # Status code response to front end endpoint
from server.exceptions import UserExists
from server.service.UserManager import *
from server.schema.user_endpoint import Input
from server.utils.authorization_utils import *


'''
Controller Functions
Front end facing layer for backend service functions

Targeted Elements
1. Registration [Working]
2. Login [Broken]
3. Siddhi - Dedicated Controllers required [ abstract wrapper functions]
'''

def Registration(information:Input):
    log.info(f'Registration Initiated : {information}')
    try:
        # converting information to dictionary format
        info_load = {
                "email": information.email,
                "password": information.password,
                "role" : "student"
                }
        register_user(info_load)
        return {"message" : "Registration completed", "status": 200}
    except UserExists as e:
        return {"message" : "Registration Failed", "status" : 404}


def Login(form_data: Input):
    '''
    Fetch UserManger from form data
    check if user exist with its parameter -> proceed to call with verification

    Use the verify function for authorizing access into application with protection of routes
    '''
    log.info("Login Function initiating")
    try:
        email = form_data.email
        unit = UserManger(email)
        if unit.existance:
            if unit.verify_credentials(form_data.password):
                return create_access_token(email)  # Access Token generated with signed
            return {"message":" Either Username or password is wrong", "status":404}
        return {"message": "User Does Not Exist, Register your self first", "status":200}
    except Exception as e:
        raise Exception(f"Login failed Exception with Problem trace of {e}")
