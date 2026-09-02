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
    variables:list[str]  # spaced variables injection required
    lower_bound:int
    upper_bound:int
    operations : str  # spaced operation element


# Question generator unit
class Prashna:
    '''
    Storing template for given question type
    Spawn question with respect to template
    evaluation service
    '''
    def __init__(self, template:QuestionTemplate):
        self.template = template

    def generate(self,groups=0, length=2):
        '''
        question generator module

        + primitive version for generating question with given labels
        + Level based complexity switching is enhacement version with this unit

        tested for generating questions with variables and grouping
        '''
        # Foundational variables for the core working
        template = self.template
        start = template.lower_bound
        end  = template.upper_bound
        operations = template.operations
        
        # random operation fetch
        operator = lambda: operations if (len(operations) == 1) else rnd.choice(operations.split(' '))

        # Operation Injection Function
        def inject_operator(string_nums):
            final_expression = ''

            for i, element in enumerate(string_nums):
                if i == len(string_nums) -1:
                    final_expression = final_expression + element
                else:
                    final_expression = final_expression + element + operator()
            return final_expression 


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
        
        if len(template.variables) >= 1:
            string_nums.extend(template.variables)  # variable listing into randomized range

        # Shuffle variable position
        rnd.shuffle(string_nums)

        # Randomized conditional grouping
        grouped_element = []
        if (groups > 0):
            for i in range(0, len(string_nums), groups):
                group_member = string_nums[i:i+groups]
                if len(group_member) < groups:
                    break
                element = f'({inject_operator(group_member)})'
                grouped_element.append(element)

            # grouping final expression | Indentation fix issue with making it return at end
            return inject_operator(grouped_element)
        elif groups > 0:
            log.warning(f"grouping number terminated")
        response = inject_operator(string_nums)
        log.info(f'Reponse for : {template} : {response}')
        return  response

