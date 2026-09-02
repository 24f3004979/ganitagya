from server.dev_log import *
from server.service.siddhi import *

def test_generator_sequence():
    # Question template making all different types of questions for generation requirements
    t = QuestionTemplate(
            question_text='generate',
            topic="Arithmatic",
            variables="x", # listing needed
            lower_bound=1,
            upper_bound=10,
            operations="+"
            )
    p = Prashna(t)
    generated_question = p.generate(level=1, length_limit=2)

    log.info(f'Siddhi Question generator output : {generated_question}')
    assert type(generated_question) == int


