from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, status
from server.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

# Internal Moudle dependency
from server.schema.user_endpoint import Input

def create_access_token(username:str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    token_data = {
            "sub":username, 
            "exp":expire
            }
    # JWT token with signed expiration timeline
    return jwt.encode(
            token_data, SECRET_KEY,
            algorithm=ALGORITHM
            )

async def get_current_user(token)->str:
    try:
        payload = jwt.decode(
                token, SECRET_KEY, algorithm=[ALGORITHM]
                )
        username:str = payload.get("sub")
        if username is None:
            raise jwt.PyJWTError
        return username
    except jwt.PyJwtError:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your Authorization token expired you can try to re-login",
                headers={"WWW-Authenticate":"Bearer"}

                )
