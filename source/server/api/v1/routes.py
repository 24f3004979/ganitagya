from typing import Annotated
from fastapi import APIRouter, status, Depends, Request
from server.api.controllers import Registration
from server.schema.user_endpoint import UserRegisterInput


router = APIRouter()

@router.get("/health")
def  health():
    return {"status":"ok", "version":"0.01"}

# Adding status code injected response for other routers
@router.post("/register")
def register(user_information:UserRegisterInput):
    return Registration(user_information)

@router.post("/login")  # FIX: Not working with this application
async def authentication(form_data: Request):
    '''
    Making simple extraction way with request object form
    '''
    data = await form_data.json()
    email = data.get("email")
    password = data.get("password")
    info = {"email":email, "password": password}

    return Login(info)
