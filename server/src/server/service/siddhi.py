'''
SiddhiEngine
Generates questions based on users previous responses
'''
from server.service.prashna import *  # Load for prashna module
from server.service.mool import *
from server.service.prashna_template import TEMPLATES

class SiddhiEngine:
    '''
    concerns : generate set of questions
    Generates question for the target topic
        - Fetch topic template
        - Initiate generator with incremental difficulty counter
    '''
    def __init__(self, target_topic):
        self.target_topic = target_topic
        self.template = TEMPLATES[target_topic]
        # Loading topic template for question generation instance

    def package_question(self, prev_response:list[bool], quantity=3) -> str:
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
            # down grade topic for lower topic ask
        elif prev_response == 0:
            # keep the same level question with downgraded hardness
        
        # Generate question with same level
    def generate(self, level):
        '''
        Generating from the template load with prashna instance with adjusting leveling functions for same level toughness and wrong answer level persistency questions

        Level upgrade ways
            + tweak length of question
            + tweak template ranges to broad integers
            + grouping terms
        '''
        question_handle = Prashna(self.template)
        pass
