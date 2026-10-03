import networkx as nx
import json
from fastapi import Depends

from server.models.student import Student
from sqlmodel import select
from server.utils.exceptions import UserDoesNotExist
from sqlalchemy.orm.attributes import flag_modified
from server.utils.watch_util import *
from server.utils.GTI import *

from server.service import RootConceptGraph

MIN_LEVEL = 1
MAX_LEVEL = 3
START_LEVEL = 1


class Vidhyarthi:
    #TODO: Need one function to check if given topic code is in students dictionary or not
    def __init__(self, student_id: int, session=None):
        self.student_id = student_id
        self.session = session

    def have_topic(self,topic):
        session = self.session

        unit = self.get_student_object()
        topics = list(unit.knowledge_graph.keys())
        if topic in topics:
            return unit.knowledge_graph[topic]  # current level
        return False # topic does not contains

    def get_student_object(self):
        '''
        get or create sequence,
        we search for existing student with given information
        or create one new student object with given id information and initiate graph
        '''
        session = self.session

        statement = select(Student).where(Student.student_id == self.student_id)
        student_unit = session.exec(statement).first()
        log.info(f"student fetch output : {student_unit}")

        if student_unit is not None:
            return student_unit

        student_unit = Student(student_id=self.student_id, knowledge_graph={})
        try:
            session.add(student_unit)
            session.commit()
            session.refresh(student_unit)
            log.info(f"Student Object initiated into student table")
            return student_unit
        except Exception as e:
            session.rollback()
            raise Exception(f"Exception in Student initiation sequence with : {e}")

    def db_handle(self, session, unit, modification=None):
        if modification is not None:
            flag_modified(unit, modification)
        try:
            session.add(unit)
            session.commit()
            session.refresh(unit)
            return True
        except Exception as e:
            session.rollback()
            log.warning(f"Student DB transaction failed with : {e}")
            raise Exception(f"Exception raised in Student Initiation with problem {e}")

    def topic_exists(self, topic_id):
        try:
            return decode(topic_id) is not None
        except Exception:
            return False

    def add_topic(self, topic_id):
        '''
        Adding topic to student graph
        1. check for topic existence
        2. db change with given information to initiate a new topic into graph
        '''
        topic_key = str(topic_id)

        if not self.topic_exists(topic_id):
            log.warning(f"Attempt to add unknown topic_id: {topic_id}")
            return None

        session = self.session
        student_object = self.get_student_object()

        if topic_key in student_object.knowledge_graph:
            return None

        student_object.knowledge_graph[topic_key] = '1'
        self.db_handle(session, student_object, "knowledge_graph")
        return True

    def update_topic(self, topic_id: int, update_modification: int):
        '''
        Simple Numerical ecoding of topics

        Fallback with breaking changes for topic udpate into student graph
        making changes to student json fetch -> type conversions required
        '''
        topic_key = str(topic_id)

        session = self.session
        student_object = self.get_student_object()

        if topic_key not in student_object.knowledge_graph:
            log.warning(f"Topic {topic_id} not present in student knowledge graph")
            return None

        current_level = int(student_object.knowledge_graph[topic_key]) # fetch level
        result = current_level + update_modification

        if (result < MIN_LEVEL) or (result > MAX_LEVEL):
            log.warning(f"Wrong Update Request recieved exceeding limits of current cap and scope")
            return None

        result = str(result)

        student_object.knowledge_graph[topic_key] = result
        self.db_handle(session, student_object, "knowledge_graph")
        return True

    def build_graph(self):
        '''
        Final Graph construction for front end units to build graph for
        Making graphical represenation of vidhyarthi current levels
        '''
        session = self.session
        student_object = self.get_student_object()
        topics = dict(student_object.knowledge_graph)

        topic_reference = {}
        for topic_id, level in topics.items():
            topic_id = int(topic_id)
            topic_name = decode(topic_id)
            if topic_name is None:
                continue
            topic_reference[topic_name] = level

        topic_lists = list(topic_reference.keys())

        student_graph = RootConceptGraph.subgraph(topic_lists).copy()

        for topic in student_graph.nodes:
            student_graph.nodes[topic]['level'] = topic_reference[topic]

        graph_data = nx.node_link_data(student_graph, edges="links")
        json_response = json.dumps(graph_data)
        return json_response
