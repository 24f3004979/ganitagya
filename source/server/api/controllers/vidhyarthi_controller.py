"""
Vidhyarthi Interface elements

Final endpoints for vidhyarthi model
Wraping with route-protection for protecting vidhyarthi-endpoint
"""

from server.service.vidhyarthi import Vidhyarthi
from server.database.setup import get_session


def fetch_topics_from_student(student_name):
    with get_session() as session:
        student = Vidhyarthi(student_id, session)
        topics = student.build_graph()
        return topics
