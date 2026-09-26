from fastapi import APIRouter, status, Request
from server.api.controllers import Registration, Login, get_role
from server.schema.user_endpoint import *
from server.utils.authorization_utils import *


router = APIRouter()

@router.get("/health")
def  health():
    return {"status":"ok", "version":"0.01"}

# Adding status code injected response for other routers
@router.post("/register")
def register(user_information:Input):
    return Registration(user_information)


@router.get("/me")
async def fetch_me(token:str):
    '''
    Fetches current name with provided token
    used for protecting routing and front end handles
    '''
    current_user = await get_current_user(token)
    return current_user


@router.get("/role")
def fetch_role(username:str):
    '''Fetch current user role for authorization for certain routs'''
    return get_role(username)  # role fetch

@router.post("/login")
async def authentication(form_data: Input):
    '''
    Login routing for verification of credentials along with token generation with user name
    '''
    print(f"login route authentication function running")
    # Refraining with direct passing through the Input strucuture for authorization case
    response = await Login(form_data)
    return response
