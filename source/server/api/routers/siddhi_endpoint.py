"""
Siddhi quiz endpoints (all protected, identity from token)

POST /quiz/start  {"topic_id": int}        -> first batch of questions
POST /quiz/next   {"answers": [int, ...]}  -> next batch, or final report
POST /quiz/end                             -> stop early, get report so far

Mount with a prefix, e.g.
    app.include_router(siddhi_router, prefix="/api/v1/siddhi")
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# adjust these import paths to where the files live in your project
from server.api.controllers.mulyankan_controller import (
    QuizNotActive,
    answer_quiz,
    end_quiz,
    start_quiz,
)
from server.api.routers.student_endpoint import get_current_student
from server.service.vidhyarthi import Vidhyarthi
from server.utils.GTI import decode

siddhi_router = APIRouter()


class StartQuizRequest(BaseModel):
    topic_id: int


class AnswerRequest(BaseModel):
    answers: list[int]


@siddhi_router.post("/quiz/start")
def quiz_start(
    body: StartQuizRequest, student: Vidhyarthi = Depends(get_current_student)
):
    # Only topics shown on this student's dashboard can be tested
    allowed = {t["topic_id"] for t in student.get_current_topics()}
    allowed |= {t["topic_id"] for t in student.get_unlocked_topics()}

    if body.topic_id not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This topic is not available for you yet",
        )

    topic = decode(body.topic_id)
    return start_quiz(student.student_id, topic)


@siddhi_router.post("/quiz/next")
def quiz_next(body: AnswerRequest, student: Vidhyarthi = Depends(get_current_student)):
    try:
        return answer_quiz(student.student_id, body.answers)
    except QuizNotActive:
        raise HTTPException(status_code=404, detail="No active quiz")
    except ValueError as e:
        # wrong number of answers; quiz stays active so the client can retry
        raise HTTPException(status_code=400, detail=str(e))


@siddhi_router.post("/quiz/end")
def quiz_end(student: Vidhyarthi = Depends(get_current_student)):
    try:
        return end_quiz(student.student_id)
    except QuizNotActive:
        raise HTTPException(status_code=404, detail="No active quiz")