# ----- Patch updated : 4 october - 2026 -----
'''
SiddhiEngine
Generates questions based on users previous responses
'''
import copy
import math

from sympy import parse_expr

from server.utils.exceptions import NotValidQuestion
from server.utils.watch_util import log
from server.service.prashna import *  # Load for prashna module
from server.service.mool import *
from server.service.prashna_template import TEMPLATES
from server.service import RootConceptGraph as rcg
from server.service.siddhi_algebra import check_question

MAX_GENERATION_ATTEMPTS = 300  # validation is cheap (~0.15 ms), a loop never recurses

# Topics where NO number may be negative anywhere in the question: literals,
# intermediate results and the final answer. Add topic names here to extend.
# Every other topic only gets the structural checks (valid syntax, no division
# by zero, runaway sizes, variables only the topic's own).
NON_NEGATIVE_TOPICS = {"Basic Arithmetic"}


def evalutate(expression):
    '''
    fails => None
    NOTE: parse_expr() uses eval. Only use it on strings the server generated,
    never on student input (grading uses siddhi_algebra.answer_is_correct).
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

    def current_symbols(self):
        '''Variables the current topic's questions may contain (e.g. ["x"]).'''
        return list(TEMPLATES[self.target_topic].variables)

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


    def generate(self):
        '''
        Makes one question for the current level and target_topic.

        Level upgrade ways
            + tweak length of question
            + tweak template ranges to broad integers
            + grouping terms

        Sequence
            tweak parameters with respect to level number
            spin an instance of prashna and generate
            validate, retry up to MAX_GENERATION_ATTEMPTS (a loop, never recursion)

        Validation depends on the topic:
            NON_NEGATIVE_TOPICS (Basic Arithmetic)
                no negative number anywhere, intermediate results included.
                The lower bound is NOT pushed negative above level 3 for these.
            topics with variables (Variable, Expression, Simplification)
                the question must contain every variable of the template and
                nothing else; there is no sign rule (Expression deliberately
                uses negative numbers).
            other numeric topics
                structural checks only.

        Raises NotValidQuestion if nothing usable came out; the caller turns
        that into a clean error response.
        '''
        level = self.level
        target = self.target_topic

        # Deep copy so the global template is never changed
        base_template = copy.deepcopy(TEMPLATES[target])
        symbols = list(base_template.variables)
        strict_non_negative = target in NON_NEGATIVE_TOPICS
        hyper_parameter = 2  # Must be int

        length = level * hyper_parameter
        # INFO : It makes too harsh questions for simple levels | needs a refactor for tuned generation
        if level > 3 and not strict_non_negative:  # only after level 3
            base_template.lower_bound -= 10 * level * hyper_parameter
        base_template.upper_bound += 2 * level * hyper_parameter
        grouping = level

        floor = 0 if strict_non_negative else None

        last_reason = "no attempt made"
        for attempt in range(1, MAX_GENERATION_ATTEMPTS + 1):
            try:
                question_unit = Prashna(copy.deepcopy(base_template))
                question_generated = question_unit.generate(grouping, length=length)
            except Exception as e:
                last_reason = f"prashna failed: {e}"
                log.debug(f"Attempt {attempt}: {last_reason}")
                continue

            usable, reason = check_question(
                question_generated,
                floor=floor,
                allowed_symbols=symbols,
                require_symbols=bool(symbols),
            )
            if usable:
                return question_generated

            last_reason = reason
            log.debug(f"Attempt {attempt}: rejected '{question_generated}' ({reason})")

        log.warning(
            f"Question generation gave up for topic '{target}' at level {level} "
            f"after {MAX_GENERATION_ATTEMPTS} attempts. Last reason: {last_reason}"
        )
        raise NotValidQuestion(
            f"No usable question for '{target}' after {MAX_GENERATION_ATTEMPTS} attempts: {last_reason}"
        )


    def bulk_generate(self, quantity:int) -> list[str]:
        questions = []
        for i in range(0, quantity):
            elem = self.generate()
            questions.append(elem)
        return questions
