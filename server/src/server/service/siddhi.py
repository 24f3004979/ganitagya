'''
SiddhiEngine
Generates questions based on users previous responses
'''
from server.service.prashna import *  # Load for prashna module
from server.service.mool import *
from server.service.prashna_template import TEMPLATES
from server.service import RootConceptGraph as rcg

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

        requests node_traversal for upgrade or downgrade with fallback for same level, saves the changes for final evaluation matrices
        '''
        if prev_response == 1:
            self.level += 2
            return self.bulk_generate(quantity, self.level)

        elif prev_response == 0:
            return self.bulk_generate(quantity, self.level)

        # Down grading current topic level
        self.topic_switch()
        self.level = 1
        return self.bulk_generate(quantity, self.level)


        # Generate question with same level
    def generate(self, level=1):
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
        '''
        target = self.target_topic
        template = TEMPLATES[target]  # question template
        hyper_parameter = 2  # Must be int

        length = level * hyper_parameter
        # range edit
        template.lower_bound -= 10 * level * hyper_parameter
        template.upper_bound += 10 * level * hyper_parameter
        grouping = level

        question_unit = Prashna(template)
        question_generated = question_unit.generate(grouping, length=length)
        return question_generated

    def bulk_generate(self, quantity:int, level:int) -> list[str]:
        questions = []
        for i in range(quantity):
            elem = self.generate(level)
            questions.append(elem)
        return questions


