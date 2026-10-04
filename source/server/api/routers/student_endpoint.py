"""
Protected routers for student information fetching endpoints

1. info fetch about student
2. graph fetch
3. dashboard (current topics + unlocked topics)

Identity always comes from the access token, never from the client.
"""

import json

from fastapi import APIRouter, HTTPException, status, Depends

from server.api.controllers.vidhyarthi_controller import fetch_user_info
from server.service.UserManager import UserManager
from server.service.vidhyarthi import Vidhyarthi
from server.utils.authorization_utils import verify_access_token
from server.utils.watch_util import log

student_router = APIRouter()


# verify_access_token returns the username from the token.
# This dependency turns it into the student's manager object.
# Plain `def` on purpose: UserManager / Vidhyarthi use blocking DB sessions,
# so FastAPI should run this in its threadpool.
def get_current_student(username: str = Depends(verify_access_token)) -> Vidhyarthi:
    user = UserManager(username)  # extract() runs in __init__
    if not user.existance:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # assumes Student.student_id == User.id
    return Vidhyarthi(user.user_object.id)


@student_router.get("/info")
def fetch_info(username: str = Depends(verify_access_token)):
    # username now comes from the token, not from a query parameter
    return fetch_user_info(username)


@student_router.get("/graph")
def my_graph(student: Vidhyarthi = Depends(get_current_student)):
    log.info("Fetching student graph data")
    # build_graph returns a JSON string; decode it so FastAPI doesn't double-encode
    return json.loads(student.build_graph())


@student_router.get("/dashboard")
def dashboard(student: Vidhyarthi = Depends(get_current_student)):
    """
    current_topics  : topics the student has and can still be tested on
    unlocked_topics : next topics the student can start
    Each item carries topic_id, which the quiz start endpoint expects.
    """
    return {
        "current_topics": student.get_current_topics(),
        "unlocked_topics": student.get_unlocked_topics(),
    }