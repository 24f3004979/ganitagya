from server.dev_log import *
from server.service.siddhi import *

def test_generator_sequence():
    # Question template making all different types of questions for generation requirements
    t = QuestionTemplate(
            question_text='generate',
            topic="Arithmatic",
            variables=["x", "4x", "4y"], # listing needed
            lower_bound=-10,
            upper_bound=10,
            operations="+ - / *"
            )
    p = Prashna(t)
    generated_question = p.generate(length=10, groups=2)

    log.info(f'Siddhi Question generator output : {generated_question}')
    assert type(generated_question) == str


