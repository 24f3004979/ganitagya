from sympy import parse_expr
import math

# from server.database import get_session
from server.models.student import Student 
from server.utils import *
from server.service.siddhi import SiddhiEngine
from server.dev_log import *

'''
Quiz Manager wrapper

No DB connection for now needs setup for DB connection setup
documentation : docs/QuizFlow.md
'''

#TODO: Need to tweak the question generation unit to not go into negetive number for foundational arithmatics :)

class SiddhiUnit:
    def __init__(self, student_id:int, starting_topic:str, number_of_questions:int=10, batch_size=2):
        self.student_id = student_id
        self.batch_size = batch_size
        self.starting_topic = starting_topic

        # Generation Sequence Numbers
        self.to_generate = number_of_questions
        self.generated_count = 0  # track generation sequence


        # Engine Element from Siddhi
        self.Engine = SiddhiEngine(starting_topic)  # Engine Initiation with topic
        
        # Inmemory Variables | Primitive version ships with
        self.WeakTopics = []
        self.StrongTopics = []

        # Reponsing interface
        self.question_index = []  # Simple internal question indexing

    def generation(self, prev_response:int):
        '''
        generate question with package
        update self value for generated_count

        Index generated question into local indexing table - evaluation

        previous response handle would take by evluation sequence
        removing generation count rails
        '''
        # Evaluation Unit would seed prev_response tag for given question
        print(f"Batch size for question generation : {self.batch_size}")
        
        # Using Package question end point for generating questions
        generated_questions = self.Engine.package_question(prev_response=prev_response, quantity=self.batch_size) # List of expressions
        log.info(f"Using Package questions endpoint for generation sequence : {generated_questions}")
        questions = []
        for _ in generated_questions:
            questions.append(_) # Internal questions listing
        self.question_index = questions # Indexing local questions list
        return questions
    
    def evaluation(self, user_response:list[int]):
        '''
        user_response {
            0: answer ,
            1: answer
        }

        Solve with sympy for given expression
        encode evaluation
        change global variables with responses

        trigger generation

        Evaluates User response and generate next sequence directions

        '''
        solution_list = []
        for expression_string in self.question_index:
            solution = None # unusual error
            try:
                result = parse_expr(expression_string)
            except Exception as e:
                raise Exception(f"Sympy problem with given question : {e}")
            solution_list.append(result)  # Solution listing

        # Simple iteration and verification
        i = 0
        validation_list = [] # 1 for correct and 0 for wrong
        for user_soln in user_response:

            if user_soln == solution_list[i]:
                validation_list.append(1)
            else:
                validation_list.append(0)

        # simple ratio based encoding logic
        log.info(f"question list : \n {self.question_index} solution list : \n {solution_list} user_solution : \n {user_response}")
        ratio = int(math.floor((sum(validation_list) / len(validation_list)) * 100))
        if ratio > 70:
            print(f"Upgrading question level")
            return 1 # upgrades level
        elif ratio < 50:
            print(f"Keeping the same level")
            return 0  # Same level
        else:
            print(f'Down grading topic switch')
            return -1
