from fastapi import APIRouter, status
from server.api.controllers import Registration
from server.schema.user_endpoint import UserRegisterInput

router = APIRouter()

@router.get("/health")
def  health():
    return {"status":"ok", "version":"0.01"}

# Adding status code injected response for other routers
@router.post("/register")
def register(user_information:UserRegisterInput):
    return Registration(user_information:UserRegisterInput)


