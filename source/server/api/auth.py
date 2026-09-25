from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer  # OAuth makes the way through which we can format the input shcema for the login purpose right ? 

# Authentication pipeline is whole broken due to miss configuration and lack of understanding about things i am using to make it , I need to read the docs to create the auth unit

# Have to lock in for wiring up the application with endpoints and front end component to wrap project first version launch
# This tells FastAPI where to look for the token (the /login endpoint)

# New Access Token Generation
def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {"sub": username, "exp": expire}
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

# Routes Protection Function for fetching current user information | what really the Depends thing does in fast api i am unknown to this thing
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        log.info(f"Payload Inspection about its data from : {payload}")
        username: str = payload.get("sub")
        if username is None:
            raise jwt.PyJWTError
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or token is invalid :) ",
            headers={"WWW-Authenticate": "Bearer"},
        )
