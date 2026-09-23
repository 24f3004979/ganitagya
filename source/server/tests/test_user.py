from server.models.user import *
from server.service.user import *

information = {
        "email" : "mail@gmail.com",
        "password" : "1234",
        "role" : "student",
        }
def test_user_creation():
    result = register_user(information)
    assert result == True
