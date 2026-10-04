"""
Final Student wrapping endpoint

1. student information
2. graph information
"""

from server.service.vidhyarthi import Vidhyarthi
from server.service.UserManager import UserManager

# Student information fetch endpoint


def fetch_user_info(user_name) -> dict:
    """
    response = {
        "id" : id,
    "graph" : topics listing
    }
    """
    initiate_object = UserManager(user_name)
    user_object = initiate_object.user_object

    id = user_object.id  # simple fetch

    # fetching topics for student
    initiating_student = Vidhyarthi(id)
    graph = initiating_student.build_graph()
    response = {"id": id, "graph": graph}
    return response
