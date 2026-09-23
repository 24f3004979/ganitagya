from server.models.user import *
from server.service.user import *

information = {
        "email" : "mailing@gmail.com",
        "password" : "1234",
        "role" : "student",
        }

def test_user_creation():
    result = register_user(information)
    assert result == True

def test_verification():
    status, role = verify_user(information)
    assert role == "student"
    assert status == True
    
