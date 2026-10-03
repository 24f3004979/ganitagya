from server.dev_log import *
from server.exceptions import UserExists, UserDoesNotExist
from server.service.UserManager import *
from server.schema.user_endpoint import Input
from server.utils.authorization_utils import *
from server.service.SiddhiManager import *

from fastapi import HTTPException, status


"""
Controller Functions
Front end facing layer for backend service functions

Targeted Elementis
1. Registration [Working]
2. Login [Broken]
3. Siddhi - Dedicated Controllers required [ abstract wrapper functions]
"""


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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Registration failed: {e}"
        )


async def Login(information: Input):  # Working tested
    log.info("Initiating LOGIN")
    try:
        email = information.email
        unit = UserManager(email)
        if unit.existance:
            if unit.verify_credentials(information.password):
                token = create_access_token(email)  # Access Token generated with signed
                return {"message": "Loging in", "token": token}
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Wrong username or password",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"User Does Not exist"
        )
    except Exception as e:
        raise Exception(f"Login failed Exception with Problem trace of {e}")


def get_role(username: str):
    try:
        unit = UserManager(username)
        if unit.existance == True:
            return {unit.user_object.role}
        else:
            return {"message": "No Existance"}
    except UserDoesNotExist:
        return {"message": "Role fetch failed | User Does not exist"}
    except Exception as e:
        raise Exception(f"Role fetch failed with problem : {e}")


def get_id(username: str):
    try:
        unit = UserManager(username)
        if unit.existance == True:
            return {unit.user_object.id}
        else:
            return {"message": "Id Fetch failed"}
    except UserDoesNotExist:
        return {"message": "Role fetch failed | User Does not exist"}
    except Exception as e:
        raise Exception(f"Role fetch failed with problem : {e}")


# ------------------ Controller Wrappers for Siddhi web interface Units ---------------------------

"""
Controller wrapper for Siddhi Engine endpoint creation
featuring
Quiz Managing functions at temporary memory level
Db-connection for syncing questions to survive reload is into next refactor targets
"""


class Mulyankan:
    """
    Fancy Naming for final Quiz mentainer controller wrapper
    Final Layer for the endpoint for given functions of siddhi module
    """

    def __init__(self, student_id: int, starting_topic: str):
        self.id = student_id
        self.starting_topic = starting_topic
        self.Manager = SiddhiUnit(student_id, starting_topic)

    def start(self):
        """
        Initiating root starting point
        """
        return self.Manager.generation(0)

    def next_question(self, previous_response):
        """
        Ends with None returning or end of quiz signal
        prev_resp [
            0: answer,
            1: answer
        ]
        """
        eval_code = self.Manager.evaluation(previous_response)
        return self.Manager.generation(eval_code)

    def get_report_information(self):
        """fetch report information with given quiz"""
        strong_topic, weak_topic = self.Manager.StrongTopics, self.Manager.WeakTopics
        info = {"strong topics": strong_topic, "weak topics": weak_topic}
        return info  # Final Result


# Memory based quiz management system
import time, threading

_QUIZZES: dict[int, tuple[Mulyankan, float]] = {}
_LOCK = threading.Lock()
TTL = 60 * 30  # 30 min idle


def _cleanup():
    now = time.time()
    for sid in [k for k, (_, t) in _QUIZZES.items() if now - t > TTL]:
        del _QUIZZES[sid]


def start_quiz(student_id: int, topic: str):
    with _LOCK:
        _cleanup()
        quiz = Mulyankan(student_id, topic)
        _QUIZZES[student_id] = (quiz, time.time())
    return quiz.start()


def answer_quiz(student_id: int, answers: list[int]):
    with _LOCK:
        entry = _QUIZZES.get(student_id)
        if not entry:
            return {"message": "No active quiz", "status": 404}
        quiz, _ = entry
        _QUIZZES[student_id] = (quiz, time.time())
    result = quiz.next_question(answers)
    if result is None:
        with _LOCK:
            _QUIZZES.pop(student_id, None)
        return {"message": "Quiz complete", "report": quiz.get_report_information()}
    return result


def abandon_quiz(student_id: int):
    with _LOCK:
        _QUIZZES.pop(student_id, None)
