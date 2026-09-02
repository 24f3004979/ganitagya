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

    def generate(self,grouping=0, length=2):
        '''
        question generator module

        + primitive version for generating question with given labels
        + Level based complexity switching is enhacement version with this unit
        '''
        # Foundational variables for the core working
        template = self.template
        start = template.lower_bound
        end  = template.upper_bound
        length = length # Length for expression
        operations = template.operations

        # Length must be stricly into a constraiined range due to complexity of choosing list
        numbers = rnd.choices(range(start, end), k=length)

        # Stringify numbers with formating negetives
        string_nums = [] # number with string format for final build
        for _ in numbers:
            element = ''
            if _ < 0:
                element = f"({_})" # Negetives in bracket
            else:
                element = str(_)
            string_nums.append(element)
        
        if len(template.variables) == 1:
            string_nums.append(template.variables)  # variable listing into randomized range

        # Shuffle variable position
        rnd.shuffle(string_nums)

        operator = lambda: operations if (len(operations) == 1) else rnd.choice(operations.split(' '))  # Returning operator for given expression buildup

        # Building final question expression with variables
        final_expression = ''
        log.info(f'Final Expression building list : {string_nums}')
        for i, element in enumerate(string_nums):
            if i == len(string_nums) -1:
                final_expression = final_expression + element
            else:
                final_expression = final_expression + element + operator()
        log.info(f"Generated expression load : {final_expression}")
        return final_expression
                
