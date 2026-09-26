from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, status
from server.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from server.dev_log import *

# Internal Moudle dependency
from server.schema.user_endpoint import Input

def create_access_token(username:str) -> str:  # working tested
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    token_data = {
            "sub":username, 
            "exp":expire
            }
    log.info(f"Token Data for inspection : {token_data}")
    # JWT token with signed expiration timeline
    token = jwt.encode(
            token_data, SECRET_KEY,
            algorithm=ALGORITHM
            )
    return token

async def get_current_user(token)->str:  # working tested
    try:
        log.info(f'config load for payload : {SECRET_KEY} along with {SECRET_KEY}')
        payload = jwt.decode(
                token, SECRET_KEY, algorithms=[ALGORITHM]
                )
        username:str = payload.get("sub")
        log.info("Not able to fetch user name with this token")
        if username is None:
            raise jwt.PyJWTError
        return username
    except jwt.PyJWTError:
        # Raising exception without authentication token being expired
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your Authorization token expired you can try to re-login",
                headers={"WWW-Authenticate":"Bearer"}

                )
