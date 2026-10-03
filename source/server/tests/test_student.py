from server.service.vidhyarthi import *
from server.api.controllers import Registration
from server.main import *
from server.service.UserManager import *
from server.schema.structure import Input
from server.utils.watch_util import *

# Making a student Profile
unit = Input(
    username='madhav@gmail.com',
    password='1234'
)

resp = Registration(unit)
new_unit = UserManager(unit.username)

# Need to create student update in table due to which non-existance error is raised
# FIX : Create trigger with user creation to update stuudent table to manual insertion for student storage system

fetch_id = new_unit.user_object.id

def test_vidhyarthi_loading():
    v = Vidhyarthi(student_id=fetch_id)
    topic_addition = v.add_topic(0)
    # check weather db gets updated with this thing
    assert topic_addition == True

def test_updating():
    v = Vidhyarthi(student_id=fetch_id)
    topic_update = v.update_topic(0, 1)
    graph = v.build_graph()
    log.info(f"Student Graph Response : {graph}")
    assert topic_update == True
