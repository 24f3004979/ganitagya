from server.dev_log import *
from server.service.siddhi import *
from .templates.siddhi_template import *
import random 

def test_generator_sequence():
    # Question template making all different types of questions for generation requirements
    t = random.choice(TEMPLATES)
    p = Prashna(t)
    generated_question = p.generate(length=10, groups=2)
    assert type(generated_question) == str


