from dataclasses import dataclass
import random as rnd
from server.dev_log import log

# Central Siddhi question listing topic list
topics = [
    "Basic Arithmetic",
    "Variable",
    "Expression",
    "Operation Order",
    "Simplification",
]

@dataclass
class QuestionTemplate:
    '''
    Question Text : generic question text which would be used into presentation of question
    variables : specials whichh would be injected during number arrangement into core expression
    bounds : Numerical Limmit for generating question
    operations : Defined operation string to use into main expression generation

    '''
    question_text:str
    topic:str
    variables:str  # spaced variables injection required
    lower_bound:int
    upper_bound:int
    operations : str  # spaced operation element


# QuestionTemplate Object
class Prashna:
    '''
    Storing template for given question type
    Spawn question with respect to template
    evaluation service
    '''
    def __init__(self, template:QuestionTemplate):
        self.template = template

    def generate(self, level:int, grouping=0, length_limit=0):
        '''
        Generation sequence for making questions
        1. randomized number generation
        2. Position numbers into expression
        3. grouping [ level based ]
        4. insert operation

        Tested for generating questions for required constraints

        Refactor required for adding variables into expression
        '''
        # Initial requied variables
        template = self.template
        start = template.lower_bound
        end = template.upper_bound

        question = '' # Final generation output

        if length_limit > 0:
            length = length_limit
        else:
            length = level * 3
        
        # RANDOM NUMBER GENERATED FOR THE CORE QUESTION GENERATION SEQUNCE
        element_listing = list(range(start, end))
        log.info(f'Before adding element into main listing : {element_listing}')
        
        listing = []
        for y in element_listing:
            listing.append(str(y))
        listing.append(template.variables)

        random_numbers = rnd.choices(listing, k=length)

        # Extending with one variables inside the sequence
        print(f"Random Number generated length : {random_numbers}")
        
        # grouping trigger
        if grouping > 0:
            pass

        def get_opr():
            if len(template.operations) == 1:
                return str(template.operations)  # terminating one single element
            oprs = template.operations.split(' ')
            return rnd.choice(oprs)
        
        # Operation Sequencing
        for i, _ in enumerate(random_numbers):
            # formating numbers for final build
            if _ < 0:
                _ = str(_)
                log.info("Initiated route with negetive number")
                Number = f"({_})" # negetive formating for question
            else:
                Number = str(_)
            
            operation = get_opr()

            # Making simple expressoin with Number and operation
            if i == len(random_numbers) -1:
                question = question + Number
            else:
                question = question + Number + operation
            log.info(f"Building expression : {question}")
            
        return question

