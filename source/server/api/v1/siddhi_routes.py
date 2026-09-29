from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from server.dev_log import *
from server.controller import start_quiz, answer_quiz, abandon_quiz  # adjust to your controller module path

router = APIRouter(prefix="/quiz", tags=["quiz"])


# ---------------- Schemas ----------------

class StartRequest(BaseModel):
    student_id: int
    topic: str = Field(..., min_length=1)


class AnswerRequest(BaseModel):
    student_id: int
    # One answer per question in the last batch, same order
    answers: list[int]


# ---------------- Routes ----------------

@router.post("/start")
def start(req: StartRequest):
    try:
        questions = start_quiz(req.student_id, req.topic)
    except KeyError:
        # TEMPLATES[topic] lookup failed in SiddhiEngine
        raise HTTPException(status_code=400, detail=f"Unknown topic: {req.topic}")
    except Exception as e:
        log.info(f"Quiz start failed: {e}")
        raise HTTPException(status_code=500, detail="Could not start quiz")

    if questions is None:
        raise HTTPException(status_code=500, detail="Question generation failed")
    return {"status": "in_progress", "questions": questions}


@router.post("/answer")
def answer(req: AnswerRequest):
    try:
        result = answer_quiz(req.student_id, req.answers)
    except Exception as e:
        log.info(f"Quiz answer failed: {e}")
        raise HTTPException(status_code=500, detail="Could not evaluate answers")

    # No active quiz
    if isinstance(result, dict) and result.get("status") == 404:
        raise HTTPException(status_code=404, detail=result["message"])

    # Quiz finished
    if isinstance(result, dict) and "report" in result:
        return {"status": "complete", "report": result["report"]}

    return {"status": "in_progress", "questions": result}


@router.delete("/abandon/{student_id}")
def abandon(student_id: int):
    abandon_quiz(student_id)
    return {"status": "abandoned"}
