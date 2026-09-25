from fastapi import APIRouter, status, Request
from server.api.controllers import Registration
from server.schema.user_endpoint import Input


router = APIRouter()

@router.get("/health")
def  health():
    return {"status":"ok", "version":"0.01"}

# Adding status code injected response for other routers
@router.post("/register")
def register(user_information:UserRegisterInput):
    return Registration(user_information)


@router.post("/login")  # FIX Iteration 1st with simple data flow -> swagger not working now :)
async def authentication(form_data: Request):
    '''
    how does really the request thing would be working with Input Based schema
    Making simple extraction way with request object form

    Swagger is no longer working to load itself
    '''
    data = await form_data.json()
    email = data.get("email")
    password = data.get("password")
    info = {"email":email, "password": password}

    return Login(info)
