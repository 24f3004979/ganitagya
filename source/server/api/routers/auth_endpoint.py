"""
Authentication end points
using controller wrapper final routing listing.

Simplified authentication and verification end points
"""

from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from server.api.controllers.authorization_controllers import Registration, Login
from server.schema.structure import Input
from server.utils.authorization_utils import get_current_user
from server.utils.watch_util import log


auth_router = APIRouter()


# Registration Handle
@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: Input):
    return Registration(data)


# Login Endpoint
@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(form_data: Input):
    response = await Login(form_data)
    return response


# Authentication bearer token injection
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@auth_router.get("/me")
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
