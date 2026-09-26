from server.service.vidhyarthi import *
from server.api.controllers import Registration
from server.main import *
from server.service.UserManager import *
from server.schema.user_endpoint import Input

# Making a student Profile
unit = Input(
    email='madhav@gmail.com',
    password='1234'
)

resp = Registration(unit)
new_unit = UserManager(unit.email)

# Need to create student update in table due to which non-existance error is raised
# FIX : Create trigger with user creation to update stuudent table to manual insertion for student storage system

fetch_id = new_unit.user_object.id

def test_vidhyarthi_loading():
    v = Vidhyarthi(student_id=fetch_id)
    topic_addition = v.add_topic(0)
    # check weather db gets updated with this thing
    assert topic_addition == True
