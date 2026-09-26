from server.dev_log import *
from fastapi.responses import JSONResponse
# from fastapi import status # Status code response to front end endpoint
from server.exceptions import UserExists, UserDoesNotExist
from server.service.UserManager import *
from server.schema.user_endpoint import Input
from server.utils.authorization_utils import *


'''
Controller Functions
Front end facing layer for backend service functions

Targeted Elementis
1. Registration [Working]
2. Login [Broken]
3. Siddhi - Dedicated Controllers required [ abstract wrapper functions]
'''

def Registration(information:Input):  # Working tested
    '''
    Need to initiate Student Table entries too along with student entry
    '''
    log.info(f'Registration Initiated : {information}')
    try:
        unit = UserManager('')
        unit.create(information)
        return {"message" : "Registration completed", "status": 200}
    except UserExists:
        return {"message" : "User Exist", "status" : 300}
    except Exception as e:
        return {"message" : "Registration Failed", "status" : 404}



async def Login(form_data: Input):  # Working tested
    '''
    Fetch UserManger from form data
    check if user exist with its parameter -> proceed to call with verification

    Use the verify function for authorizing access into application with protection of routes

    pydantic class Not fully defined Error Being traced
    '''
    log.info("Login Function initiating")
    try:
        email = form_data.email
        print(f"Executing Login Controller function with email : {email}")
        unit = UserManager(email)
        if unit.existance:
            if unit.verify_credentials(form_data.password):
                token = create_access_token(email)  # Access Token generated with signed
                return token
            return {"message":" Either Username or password is wrong", "status":404}
        return {"message": "User Does Not Exist, Register your self first", "status":200}
    except Exception as e:
        raise Exception(f"Login failed Exception with Problem trace of {e}")

def get_role(username:str):
    try:
        unit = UserManager(username)
        if (unit.existance == True):
            return {unit.user_object.role}
        else:
            return {"message":"No Existance"}
    except UserDoesNotExist:
        return {"message" : "Role fetch failed | User Does not exist"}
    except Exception as e:
        raise Exception(f"Role fetch failed with problem : {e}")
