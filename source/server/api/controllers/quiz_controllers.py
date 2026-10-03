'''
Quiz Controllers
With Dedicated functions to serve quiz related endpoints
'''
from server.service.SiddhiManager import SiddhiUnit


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
