'''
Student Mangement
Functions
1. Add new topic to graph | Update level of a given topic id
2. fetch student graph and build with root reference
'''
from fastapi import Depends

from server.models.student import Student, status 
from sqlmodel import select
from server.database import get_session
from server.exceptions import UserDoesNotExist
from sqlalchemy.orm.attributes import flag_modified

class Vidhyarthi:
    '''
    Simple student abstraction function

    Functions
    1. Adding new topic to student graph
    2. graph building information -> front end api serving endpoint
    '''
    def __init__(self, student_id:int):
        self.student_id = student_id  # we can fetch student object form DB with geting function

    def get_student_object(self):

        statement = select(Student).where(Student.student_id == self.student_id)

        with next(get_session()) as session:
            try:
                student_unit = session.exec(statement).first()
                if student_unit is None:
                    raise UserDoesNotExist
                return student_unit  # referencing from db object fetch
                
            except UserDoesNotExist:
                raise UserDoesNotExist
            except Exception as e:
                raise Exception(f"Exception in Student initiation sequence with : {e}")

    def add_topic(self, topic_id):
        '''
        First simply fetch topic id from global helping indexing function for given topic
        make sure to handle missing topic problem if wrong topic passed different from global level
        '''
        student_object = self.get_student_object()
        student_object.knowledge_graph[topic_id] = status.STARTED  # FIX: Add enum object at status with student

        flag_modified(student_object, "knowledge_graph")
        try:
            with next(get_session()) as session:
                session.add(student_object)
                session.commit()
                session.refresh(student_object)
                return True
        except Exception as e:
            raise Exception(f"Terminating student topic addition with {e}")
