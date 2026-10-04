from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from server.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

from server.service.UserManager import UserManager
from server.utils.exceptions import UserDoesNotExist
from server.utils.watch_util import log


def create_access_token(username: str) -> str:  # working tested
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    token_data = {"sub": username, "exp": expire}
    log.info(f"Token Data for inspection : {token_data}")
    # JWT token with signed expiration timeline
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def get_current_user(token) -> str:  # working tested
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            log.info(f"Token verification failed :{payload}")
            raise jwt.PyJWTError
        log.info(f"Token verification successful : {payload}")
        return username
    except jwt.PyJWTError:
        # Raising exception without authentication token being expired
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your Authorization token expired you can try to re-login",
            headers={"WWW-Authenticate": "Bearer"},
        )


# fetch currrent user information


def get_role(username: str):
    """
    Input : str
    If input is given empty -> returns None
    If user does not exist -> Exception raised for non-Existence
    """
    try:
        if username == "":
            return None
        unit = UserManager(username)
        if unit.existance == True:
            return {unit.user_object.role}
        else:
            return {"message": "No Existance"}
    except UserDoesNotExist:
        return {"message": "Role fetch failed | User Does not exist"}


def get_id(username: str):
    """
    Make One universal User information fetching unit for fetching information about user into one go

    """
    try:
        if username == "":
            return None
        unit = UserManager(username)
        if unit.existance == True:
            return {unit.user_object.id}
        else:
            return {"message": "Id Fetch failed"}
    except UserDoesNotExist:
        return {"message": "Role fetch failed | User Does not exist"}


# ----------------------- Unified Token verification utility -----------------------

security = HTTPBearer()


async def verify_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Unified interface to receive requests, extract, and verify the access_token.
    Raises 401 HTTPException if the token is invalid or expired.
    """
    token = credentials.credentials
    try:
        # Decode and verify the JWT payload
        username = await get_current_user(token)  # Using another utility for verification
        log.info(f"Token verification successful for user: {username}")
        return username  # returning username with fetch success
    except jwt.ExpiredSignatureError:
        log.warning(f"Token has expired with payload : {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        log.warning(f"Invalid token with payload : {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
