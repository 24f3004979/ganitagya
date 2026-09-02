from server.service.siddhi import QuestionTemplate

'''
Loading Template for listing out question moduler
'''

TEMPLATES: list[QuestionTemplate] = [
    QuestionTemplate(
        question_text="Evaluate the following expression:",
        topic="Basic Arithmetic",
        variables=[],
        lower_bound=1,
        upper_bound=20,
        operations="+ -",
    ),
    QuestionTemplate(
        question_text="Simplify the expression by combining the given variable with the numbers:",
        topic="Variable",
        variables=["x"],
        lower_bound=1,
        upper_bound=10,
        operations="+ -",
    ),
    QuestionTemplate(
        question_text="Write the value of the following expression:",
        topic="Expression",
        variables=["y"],
        lower_bound=-10,
        upper_bound=10,
        operations="+ - *",
    ),
    QuestionTemplate(
        question_text="Apply the correct order of operations to solve:",
        topic="Operation Order",
        variables=[],
        lower_bound=1,
        upper_bound=15,
        operations="+ - * /",
    ),
    QuestionTemplate(
        question_text="Simplify the following expression as far as possible:",
        topic="Simplification",
        variables=["x", "y"],
        lower_bound=1,
        upper_bound=12,
        operations="+ -",
    ),
]
