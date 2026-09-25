from fastapi import APIRouter, status, Request
from server.api.controllers import Registration, Login
from server.schema.user_endpoint import *


router = APIRouter()

@router.get("/health")
def  health():
    return {"status":"ok", "version":"0.01"}

# Adding status code injected response for other routers
@router.post("/register")
def register(user_information:Input):
    return Registration(user_information)


@router.post("/login")
async def authentication(form_data: Input):
    '''
    Authentication routing,
    User credentials verification and returning signed token string
    '''
    print(f"login route authentication function running")
    # Refraining with direct passing through the Input strucuture for authorization case
    return Login(form_data)
