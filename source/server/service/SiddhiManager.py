import math

# from server.database import get_session
from server.utils.GTI import *
from server.service.vidhyarthi import Vidhyarthi

from server.utils import *
from server.service.siddhi import SiddhiEngine, evalutate
from server.dev_log import *
from server.database import get_session


'''
Quiz Manager wrapper

No DB connection for now needs setup for DB connection setup
documentation : docs/QuizFlow.md
'''

class SiddhiUnit:
    def __init__(self, student_id:int, starting_topic:str, number_of_questions:int=10, batch_size=2):
        self.student_id = student_id
        self.batch_size = batch_size
        self.starting_topic = starting_topic

        self.vidhyarthi_unit = Vidhyarthi(student_id=student_id)

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
        if self.generated_count > self.to_generate:
            return None # Over fow Need to be taken care with handler about generation stoping limmit

        # Using Package question end point for generating questions
        generated_questions = self.Engine.package_question(prev_response=prev_response, quantity=self.batch_size) # List of expressions
        log.info(f"Using Package questions endpoint for generation sequence : {generated_questions}")
        questions = []
        for _ in generated_questions:
            questions.append(_) # Internal questions listing

        log.info(f"Questions generated : {questions}")
        self.question_index = questions # Indexing local questions list
        self.generated_count += self.batch_size # updating questions output
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
                result = evalutate(expression_string)
            except Exception as e:
                raise Exception(f"Sympy problem with given question : {e}")
            solution_list.append(result)  # Solution listing

        validation_list = [] # 1 for correct and 0 for wrong
        log.info(f'Validation and solution listing : {user_response} with solution list : {solution_list}')

        for user_solution, actual_answer in zip(user_response, solution_list):
            if user_solution == actual_answer:
                validation_list.append(1)
            else:
                validation_list.append(0)

        # simple ratio based encoding logic
        log.info(f"question list : \n {self.question_index} solution list : \n {solution_list} user_solution : \n {user_response}")
        ratio = int(math.floor((sum(validation_list) / len(validation_list)) * 100))

        #TODO: Upgrade a down grade this quiz generator internal & student DB through StudentManger Object handle
        '''
        with vidhyarthi_unit we can tweak student object
        fetch current topic from engine variable
        with self engine we can tweak the question level
        tweaking topic change call -> Note transaction in current object module

        Dedicated Student handle for this case is required for gearing up student DB round
        '''
        current_topic = self.Engine.target_topic

        if ratio > 70:
            log.info("Gearig Up")
            self.StrongTopics.append(current_topic)
            self.gear(+1, topic=current_topic)
            return 1
        elif ratio < 50:
            log.info("Gearing Down")
            self.gear(-1, topic=current_topic)
            return -1
        else:
            log.info("Keeping Same Level")
            return 0

    def gear(self, gear: int, topic: str):
        with get_session() as session:
            self.vidhyarthi_unit.session = session
            self.vidhyarthi_unit.get_student_object()

            topic_id = encode(topic)
            level = self.vidhyarthi_unit.have_topic(str(topic_id))
            if not level:
                self.vidhyarthi_unit.add_topic(topic_id)
                level = '1'

            new_level = int(level) + gear
            if new_level < 1:
                self.WeakTopics.append(topic)
                self.Engine.topic_switch()
                return
            if new_level > 3:
                return

            self.vidhyarthi_unit.update_topic(topic_id, gear)
            self.Engine.level += gear
