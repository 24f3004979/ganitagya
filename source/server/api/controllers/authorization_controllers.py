"""
Controller function for authentication endpoints for ganitagya

Working Regisration and login controllers
"""

from server.utils.watch_util import *
from server.utils.exceptions import UserExists
from server.service.UserManager import UserManager
from server.schema.structure import Input
from server.utils.authorization_utils import create_access_token, get_current_user
from server.service.SiddhiManager import *

from fastapi import HTTPException, status


def Registration(information: Input):
    log.info(
        "Registration Initiated"
    )  # avoid logging the full input, it contains the password
    try:
        unit = UserManager("")
        unit.create(information)
        return {"message": "Registration successful"}
    except UserExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    except Exception as e:
        log.info("Registration failed: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Registration failed: {e}"
        )


async def Login(information: Input):
    unit = UserManager(information.username)

    if not unit.existance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not exist",
        )

    if not unit.verify_credentials(information.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password",
        )

    token = create_access_token(information.username)
    return {"message": "Logging in", "token": token}
