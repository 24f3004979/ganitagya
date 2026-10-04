import math

from server.service.siddhi import SiddhiEngine
from server.service.siddhi_algebra import answer_is_correct
from server.service.vidhyarthi import Vidhyarthi
from server.utils.GTI import encode
from server.utils.watch_util import log

"""
Quiz Manager wrapper
documentation : docs/QuizFlow.md
"""


class SiddhiUnit:
    def __init__(
        self,
        student_id: int,
        starting_topic: str,
        number_of_questions: int = 10,
        batch_size=2,
    ):
        self.student_id = student_id
        self.batch_size = batch_size
        self.starting_topic = starting_topic

        # Vidhyarthi manages its own sessions now, nothing to pass in
        self.vidhyarthi_unit = Vidhyarthi(student_id=student_id)

        # Generation sequence numbers
        self.to_generate = number_of_questions
        self.generated_count = 0  # track generation sequence

        # Engine element from Siddhi
        self.Engine = SiddhiEngine(starting_topic)

        # In-memory variables | primitive version ships with
        self.WeakTopics = []
        self.StrongTopics = []

        # Responding interface
        self.question_index = []  # questions of the current batch
        self.last_validation = []  # 1 correct / 0 wrong for the last evaluated batch

    def generation(self, prev_response: int):
        """
        Generate the next batch of questions through the engine package endpoint.
        Returns None once the requested number of questions has been generated.
        """
        # `>=` (was `>`): with 10 questions and batches of 2 the old check
        # produced a sixth batch.
        if self.generated_count >= self.to_generate:
            return None

        questions = list(
            self.Engine.package_question(
                prev_response=prev_response, quantity=self.batch_size
            )
        )
        log.info(f"Questions generated : {questions}")

        self.question_index = questions
        self.generated_count += self.batch_size
        return questions

    def evaluation(self, user_response: list):
        """
        user_response : answers (text or numbers) in the same order as the last
        batch of questions

        Grade with siddhi_algebra, then gear the student map.
        Returns 1 (gear up), -1 (gear down) or 0 (no change); the value feeds
        straight into generation() as prev_response.
        """
        if not self.question_index:
            raise ValueError("No questions have been generated yet")
        if len(user_response) != len(self.question_index):
            raise ValueError(
                f"Expected {len(self.question_index)} answers, got {len(user_response)}"
            )

        # Variables the current topic may use. The engine's target topic only
        # changes after this method (in package_question), so it is still the
        # topic these questions were generated for.
        symbols = self.Engine.current_symbols()

        validation_list = []  # 1 for correct and 0 for wrong
        for question, answer in zip(self.question_index, user_response):
            # answers can be "5", "7/2", "x - 3", "2x + 1"; never goes through eval
            correct, reason = answer_is_correct(question, str(answer), symbols)
            log.info(f"Graded '{question}' | answer '{answer}' | {correct} {reason}")
            validation_list.append(1 if correct else 0)
        self.last_validation = validation_list

        ratio = int(math.floor((sum(validation_list) / len(validation_list)) * 100))
        current_topic = self.Engine.target_topic

        if ratio > 70:
            log.info("Gearing Up")
            self.StrongTopics.append(current_topic)
            self.gear(+1, topic=current_topic)
            return 1
        elif ratio < 50:
            log.info("Gearing Down")
            self.gear(-1, topic=current_topic)
            return -1
        else:
            log.info("No changes to Levels and engine")
            return 0

    def gear(self, gear_number: int, topic: str):
        """
        Updates the STUDENT map only. This is the ONLY place in the quiz chain
        that writes to the student DB.

        WHEN A TOPIC IS ADDED to the student's knowledge_graph:
          - evaluation() calls gear() only for a decisive batch
            (ratio > 70 -> +1, ratio < 50 -> -1). A 50-70% batch never gets
            here, so nothing is written, even for a brand new topic.
          - The topic is the engine's CURRENT target topic, which can differ
            from the starting topic after a topic switch.
          - If the student doesn't have that topic yet, it is added at
            START_LEVEL ("1") first, then the level change is applied:
                +1 -> ends at level 2
                -1 -> stays at level 1 (MIN_LEVEL) and the topic is recorded
                      in WeakTopics
          - Starting, ending or abandoning a quiz never adds a topic.
        See docs/QuizFlow.md ("When a topic is added to the student DB").

        Engine difficulty and topic switching are done by
        Engine.package_question(prev_response), which generation() calls right
        after evaluation(). Doing it here as well caused the "shoots up too
        high" problem (+1 here and +2 there) and a double topic switch on
        gear down.
        """
        topic_id = encode(topic)

        # This unit lives across several requests, so refresh the snapshot
        self.vidhyarthi_unit.extract()
        level = self.vidhyarthi_unit.get_topic_level(topic_id)

        # get_topic_level returns False when the student doesn't have the topic.
        # (The old code did str(False) == "False", which is truthy, so a new
        # topic was never added.)
        if level is False:
            self.vidhyarthi_unit.add_topic(topic_id)
            level = "1"

        new_level = int(level) + gear_number
        if new_level < 1:
            self.WeakTopics.append(topic)
            # no DB change below MIN_LEVEL; change_topic_level just refuses

        self.vidhyarthi_unit.change_topic_level(topic_id, gear_number)
