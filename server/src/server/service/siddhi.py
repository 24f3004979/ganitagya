
# Central Siddhi question listing topic list
topics = [
    "Basic Arithmetic",
    "Variable",
    "Expression",
    "Operation Order",
    "Simplification",
]

class QuestionTemplate:
    '''
    Foundational Question template

    terms : element of question
    generation_variable : target variables
    question_variables : mathematical variables
    '''
    pass 

# QuestionTemplate Object
class Prashna:
    '''
    Storing template for given question type
    Spawn question with respect to template
    evaluation service
    '''
    def __init__(self, topic_name:str):
        self.topic = topic_name




