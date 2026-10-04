import json

import networkx as nx
from sqlalchemy.orm.attributes import flag_modified
from sqlmodel import Session, select

from server.models.student import Student
from server.service import RootConceptGraph
from server.utils.GTI import *
from server.utils.watch_util import *
from server.database.setup import engine

MIN_LEVEL = 1
MAX_LEVEL = 3
START_LEVEL = "1"

# A topic unlocks when every prerequisite is known at this level or higher.
UNLOCK_MIN_LEVEL = 1


class Vidhyarthi:
    """
    Student manager. Works like UserManager:
    initiate with student_id -> extract() syncs with DB -> use methods.
    Every method opens (and closes) its own session.

    Renames from the previous version:
        have_topic    -> get_topic_level
        topic_exists  -> is_valid_topic
        update_topic  -> change_topic_level
        distroy       -> destroy
    """

    def __init__(self, student_id: int):
        self.student_id = student_id
        self.existence = False
        self.student_object = None

        self.extract()  # Sync with DB for extraction of student information

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _fetch(self, session):
        statement = select(Student).where(Student.student_id == self.student_id)
        return session.exec(statement).first()

    def _fetch_or_create(self, session):
        """
        Get existing student row, or create one with an empty graph.
        Must be called inside an open session; commits only on creation.
        """
        student_unit = self._fetch(session)
        if student_unit is not None:
            return student_unit

        student_unit = Student(student_id=self.student_id, knowledge_graph={})
        session.add(student_unit)
        session.commit()
        session.refresh(student_unit)
        log.info(f"Student Object initiated into student table : {self.student_id}")
        return student_unit

    def _save(self, session, unit, modified_field=None):
        """Commit a change on `unit`, and keep the cached object in sync."""
        if modified_field is not None:
            flag_modified(unit, modified_field)
        session.add(unit)
        session.commit()
        session.refresh(unit)
        self.student_object = unit
        self.existence = True

    def _known_levels(self):
        """
        Fresh read from DB.
        Returns {topic_name: level_int} for every topic the student has.
        Unknown / undecodable topic ids are skipped.
        """
        with Session(engine) as session:
            student_unit = self._fetch_or_create(session)
            raw = dict(student_unit.knowledge_graph)

        levels = {}
        for topic_id, level in raw.items():
            name = decode(int(topic_id))
            if name is None:
                continue
            levels[name] = int(level)
        return levels

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def extract(self):
        """
        Checks if this student exists in DB (read only, does not create).
        Sets self.existence and self.student_object.
        """
        with Session(engine) as session:
            try:
                student_unit = self._fetch(session)
                if student_unit is None:
                    self.existence = False
                    self.student_object = None
                    return
                self.student_object = student_unit
                self.existence = True
            except Exception as e:
                log.info(f"Exception Raised as {e} at Student Extraction")

    def create(self):
        """
        Creates the student row (with empty knowledge graph) if it is missing.
        Safe to call multiple times.
        """
        with Session(engine) as session:
            try:
                student_unit = self._fetch_or_create(session)
                self.student_object = student_unit
                self.existence = True
            except Exception as e:
                session.rollback()
                raise Exception(f"Exception in Student initiation sequence with : {e}")

    def get_topic_level(self, topic):
        """Returns current level of topic if student has it, else False."""
        if not self.existence:
            return False
        graph = self.student_object.knowledge_graph
        return graph[str(topic)] if str(topic) in graph else False

    def is_valid_topic(self, topic_id):
        """True if topic_id exists in the global topic index (not student specific)."""
        try:
            return decode(topic_id) is not None
        except Exception:
            return False

    def add_topic(self, topic_id):
        """
        Adding topic to student graph
        1. check for topic existence
        2. db change to initiate a new topic into graph
        (student row is created automatically if missing)
        """
        topic_key = str(topic_id)

        if not self.is_valid_topic(topic_id):
            log.warning(f"Attempt to add unknown topic_id: {topic_id}")
            return None

        with Session(engine) as session:
            try:
                student_unit = self._fetch_or_create(session)

                if topic_key in student_unit.knowledge_graph:
                    self.student_object = student_unit
                    self.existence = True
                    return None

                student_unit.knowledge_graph[topic_key] = START_LEVEL
                self._save(session, student_unit, "knowledge_graph")
                return True
            except Exception as e:
                session.rollback()
                log.warning(f"Student DB transaction failed with : {e}")
                raise Exception(
                    f"Exception raised in Student add_topic with problem {e}"
                )

    def change_topic_level(self, topic_id: int, level_change: int):
        """
        Move a topic level up or down by `level_change`.
        Levels are stored as strings in the JSON column -> type conversion needed.
        """
        topic_key = str(topic_id)

        with Session(engine) as session:
            try:
                student_unit = self._fetch(session)
                if student_unit is None:
                    log.warning(f"Student {self.student_id} does not exist")
                    return None

                if topic_key not in student_unit.knowledge_graph:
                    log.warning(
                        f"Topic {topic_id} not present in student knowledge graph"
                    )
                    return None

                current_level = int(student_unit.knowledge_graph[topic_key])
                result = current_level + level_change

                if result < MIN_LEVEL or result > MAX_LEVEL:
                    log.warning(
                        "Wrong Update Request received exceeding limits of current cap and scope"
                    )
                    return None

                student_unit.knowledge_graph[topic_key] = str(result)
                self._save(session, student_unit, "knowledge_graph")
                return True
            except Exception as e:
                session.rollback()
                log.warning(f"Student DB transaction failed with : {e}")
                raise Exception(
                    f"Exception raised in Student change_topic_level with problem {e}"
                )

    def get_current_topics(self):
        """
        Topics the student already has and can still be tested on
        (level below MAX_LEVEL).
        Returns [{"topic_id", "name", "level"}, ...]
        """
        result = []
        for name, level in self._known_levels().items():
            if level >= MAX_LEVEL:
                continue
            result.append({"topic_id": encode(name), "name": name, "level": level})
        return result

    def get_unlocked_topics(self):
        """
        Next topics the student can start testing.
        A topic is unlocked when it is not yet known and ALL its prerequisites
        are known at UNLOCK_MIN_LEVEL or higher.

        Assumes an edge A -> B in RootConceptGraph means "A is prerequisite of B".
        Topics with no prerequisites are unlocked from the start.
        Returns [{"topic_id", "name"}, ...]
        """
        known = self._known_levels()
        unlocked = []

        for topic in RootConceptGraph.nodes:
            if topic in known:
                continue
            prerequisites = list(RootConceptGraph.predecessors(topic))
            if all(known.get(p, 0) >= UNLOCK_MIN_LEVEL for p in prerequisites):
                unlocked.append({"topic_id": encode(topic), "name": topic})
        return unlocked

    def build_graph(self):
        """
        Final graph construction for front end.
        Graphical representation of student's current levels.
        """
        with Session(engine) as session:
            student_unit = self._fetch_or_create(session)
            topics = dict(student_unit.knowledge_graph)

        topic_reference = {}
        for topic_id, level in topics.items():
            topic_name = decode(int(topic_id))
            if topic_name is None:
                continue
            topic_reference[topic_name] = level

        student_graph = RootConceptGraph.subgraph(list(topic_reference.keys())).copy()

        for topic in student_graph.nodes:
            student_graph.nodes[topic]["level"] = topic_reference[topic]

        graph_data = nx.node_link_data(student_graph, edges="links")
        return json.dumps(graph_data)

    def destroy(self):
        """Delete the student row."""
        with Session(engine) as session:
            try:
                student_unit = self._fetch(session)
                if student_unit is None:
                    self.existence = False
                    raise UserDoesNotExist
                session.delete(student_unit)
                session.commit()
                self.existence = False
                self.student_object = None
                log.info(f"Student deleted with id : {self.student_id}")
            except UserDoesNotExist:
                raise
            except Exception as e:
                session.rollback()
                raise Exception(f"Deletion Failed with exception : {e}")