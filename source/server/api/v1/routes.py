from fastapi import APIRouter, status, HTTPException, Depends
from server.api.controllers import Registration, Login, get_role, get_id
from server.schema.user_endpoint import *
from server.utils.authorization_utils import *
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "version": "0.01"}


# Adding status code injected response for other routers
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: Input):
    return Registration(data)


# Authentication bearer token injection
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/me")
async def fetch_me(token: str = Depends(oauth2_scheme)):
    """
    Fetches current name with provided token from the Authorization header.
    """
    current_user = await get_current_user(token)
    log.warning(f"Me end point user information fetch response : {current_user}")
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )
    return current_user


@router.get("/fetch-id")
def fetch_id(user_name: str):
    return get_id(user_name)


@router.get("/role")
def fetch_role(username: str):
    """Fetch current user role for authorization for certain routs"""
    return get_role(username)  # role fetch


@router.post("/login")
async def authentication(form_data: Input):
    """
    Login routing for verification of credentials along with token generation with user name
    """
    print(f"login route authentication function running")
    # Refraining with direct passing through the Input strucuture for authorization case
    response = await Login(form_data)
    return response
