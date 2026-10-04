"""
Quiz Controllers
With dedicated functions to serve quiz related endpoints
"""

import threading
import time

from server.service.SiddhiManager import SiddhiUnit


class QuizNotActive(Exception):
    """Raised when a student has no running quiz (never started, ended, or expired)."""


class Mulyankan:
    """
    Final layer for the endpoints over the siddhi module.
    One instance == one running quiz for one student.
    """

    def __init__(self, student_id: int, starting_topic: str):
        self.id = student_id
        self.starting_topic = starting_topic
        self.Manager = SiddhiUnit(student_id, starting_topic)
        self.lock = threading.Lock()  # stops double-submit races on one quiz

    def start(self):
        """Initiating root starting point"""
        return self.Manager.generation(0)

    def next_question(self, previous_response: list[int]):
        """
        Evaluates previous answers, then generates the next batch.
        Returns None at the end of the quiz.
        """
        eval_code = self.Manager.evaluation(previous_response)
        return self.Manager.generation(eval_code)

    def progress(self):
        return {
            "generated": self.Manager.generated_count,
            "total": self.Manager.to_generate,
        }

    def get_report_information(self):
        """Report for the quiz so far (duplicates removed, order kept)."""
        return {
            "strong_topics": list(dict.fromkeys(self.Manager.StrongTopics)),
            "weak_topics": list(dict.fromkeys(self.Manager.WeakTopics)),
        }


# ---------------------------------------------------------------------- #
# Memory based quiz registry
# NOTE: lives inside one process. With several uvicorn/gunicorn workers a
# student's requests can land on different workers and lose the quiz.
# Run a single worker for now, or move this to Redis/DB later.
# ---------------------------------------------------------------------- #
_QUIZZES: dict[int, tuple[Mulyankan, float]] = {}
_LOCK = threading.Lock()
TTL = 60 * 30  # 30 min idle


def _cleanup():
    """Call with _LOCK held."""
    now = time.time()
    for sid in [k for k, (_, t) in _QUIZZES.items() if now - t > TTL]:
        del _QUIZZES[sid]


def start_quiz(student_id: int, topic: str) -> dict:
    # Build and generate outside the lock; it hits the DB and sympy.
    quiz = Mulyankan(student_id, topic)
    questions = quiz.start()
    with _LOCK:
        _cleanup()
        _QUIZZES[student_id] = (quiz, time.time())  # restarting replaces old quiz
    return {"topic": topic, "questions": questions, "progress": quiz.progress()}


def answer_quiz(student_id: int, answers: list[int]) -> dict:
    with _LOCK:
        entry = _QUIZZES.get(student_id)
        if entry is None or time.time() - entry[1] > TTL:
            _QUIZZES.pop(student_id, None)
            raise QuizNotActive
        quiz, _ = entry
        _QUIZZES[student_id] = (quiz, time.time())

    with quiz.lock:
        result = quiz.next_question(answers)  # ValueError on bad answer count
        previous = quiz.Manager.last_validation  # 1 = correct, 0 = wrong, per question

    if result is None:
        with _LOCK:
            _QUIZZES.pop(student_id, None)
        return {
            "completed": True,
            "previous_result": previous,
            "report": quiz.get_report_information(),
        }

    return {
        "completed": False,
        "previous_result": previous,
        "questions": result,
        "progress": quiz.progress(),
    }


def end_quiz(student_id: int) -> dict:
    """Stop the quiz early and return the report collected so far."""
    with _LOCK:
        entry = _QUIZZES.pop(student_id, None)
    if entry is None:
        raise QuizNotActive
    quiz, _ = entry
    return {"completed": False, "report": quiz.get_report_information()}