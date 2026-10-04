'''
SiddhiEngine
Generates questions based on users previous responses
'''
from sympy import parse_expr
import math
import copy

from server.utils.exceptions import NotValidQuestion
from server.service.prashna import *  # Load for prashna module
from server.service.mool import *
from server.service.prashna_template import TEMPLATES
from server.service import RootConceptGraph as rcg

def evalutate(expression):
    '''
    fails => None
    '''
    try:
        result = parse_expr(expression)
        return result
    except Exception as e:
        log.info(f'Evaluation failed with : {e}')
        return None


class SiddhiEngine:
    '''
    concerns : generate set of questions
    Generates question for the target topic
        - Fetch topic template
        - Initiate generator with incremental difficulty counter

    TIP : If student bounce back with consiqutive right questions then take level to started topic
    '''
    def __init__(self, target_topic):
        self.target_topic = target_topic
        self.template = TEMPLATES[target_topic]
        # Loading topic template for question generation instance
            
        # Internal functions would manage these transactions
        self.level = 1
        self.trace = []

    def topic_switch(self):
        topic_list = rcg.downgrade_concept(self.target_topic)
        if topic_list == []:
            return # No changes due to dead end
        self.trace.append(self.target_topic)
        self.target_topic = topic_list[0]


    def package_question(self, prev_response:int , quantity=3) -> list[str]:
        '''
        Simple generation logic with prashna module
        previous_respons : 
        simple convention map 
        {
            both_wrong : -1
            one_wrong : 0
            both_right : 1
        }
        quantity : questions to produce

        Encodes for packaging questions with prev-response
        1: both right +2 level increment
        0: one right one wrong same level
        -1: topic down grades for generating questions

        '''
        if prev_response == 1:
            self.level += 2
            return self.bulk_generate(quantity)

        elif prev_response == 0:
            return self.bulk_generate(quantity)

        # Down grading current topic level
        self.topic_switch()
        self.level = 1
        return self.bulk_generate(quantity)


    # Generate question with same level
    def generate(self):
        '''
        Just Makes the question with given level details
        with using target_topic at class level
        Level upgrade ways
            + tweak length of question
            + tweak template ranges to broad integers
            + grouping terms
        Making simple generations for the given constraints

        Sequence

        tweak parameter with respect to level number
        spin instance for prashna
        generate

        ------
        Issue -> Raising max depth reached with variable questions
        sympy variable solving service required
        '''
        level = self.level
        target = self.target_topic
        # Making deep copy from gloabal variable to not change it on the go 
        template = copy.deepcopy(TEMPLATES[target])
        hyper_parameter = 2  # Must be int

        length = level * hyper_parameter
        #INFO : It makes too harsh questions for simple levels | Need a refactor for designed tuned generation sequence
        if level > 3: # only after level 3
            template.lower_bound -= 10 * level * hyper_parameter # Required for simple basic arithmatic guardrailing
        template.upper_bound += 2 * level * hyper_parameter  # Downgrading a bit for simple generations
        grouping = level

        question_unit = Prashna(template)
        question_generated = question_unit.generate(grouping, length=length)
        
        #INFO: Basic Guard rail for not generating non-existent questions also negetives for small levels

        try:
            result = evalutate(question_generated)
            if result < 0:
                raise NotValidQuestion
        except NotValidQuestion: 
            log.info(f'Recursive call for generation due to incorrect question : {question_generated}')
            return self.generate()

        except Exception as e:
            log.info(f'May be Non-solvable question : {e}')
            log.info(f'Recursive call for generation due to incorrect question : {question_generated}')
            return self.generate()
        return question_generated

    def bulk_generate(self, quantity:int) -> list[str]:
        questions = []
        for i in range(0, quantity):
            elem = self.generate()
            questions.append(elem)
        return questions


