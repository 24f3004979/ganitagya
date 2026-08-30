'''
Root Graph
information repository
    + directions driving core component
    + Dependency traversal
'''
from typing import Any, Iterable
import networkx as nx 

class TopicGraph(nx.DiGraph):
    '''
    Root repository for core dependency structure
    relations between topics
    fetch traversal and direction calls
    '''

    # Boot Straping root node for information cluster guide
    def add_topic(self, topic:str, **attrs:Any) -> "TopicGraph":
        if topic in self:
            raise Exception("Topic Already Exists into main graph")
        self.add_node(name, **attrs)
        return self  # New way for defining functions

    def add_dependency(self, prerequisite:str, topic:str) -> "TopicGraph":
        '''
        Adding dependency to the root graphing node
        with fallback with exception of cyclic exception
        '''
        had_prereq = prerequisite in self
        had_topic = topic in self

        # Loading Fall back with cyclic crash rollback
        if not nx.is_directed_acyclic_graph(self):
            self.remove_edge(prerequisite, topic)
            if not had_prereq:
                self.remove_node(prerequisite)
            if not had_topic:
                self.remove_node(topic)
            raise Exception("Cyclic dependency issues with the core graph")
        # Rollback with cyclic Dependency Issue with root graph construction
        return self
    
    def add_dependencies(self, prerequisities:Iterable[str], topic:str) -> "TopicGraph":
        for prereq in prerequisities:
            self.add_dependency(prereq, topic)
        return self

    # CORE QUERY API ENDPOINT
    def _require(self, topic) -> None:
        if topic not in self:
            raise Exception("Topic Not found With our Root Node :)")

    def downgrade_topic(self, topic:str, recursive:bool = False) -> list[str]:
        '''recursive:true -> List of all required topics | just one'''
        self._require(topic)
        if recursive:
            return list(nx.ancestors(self, topic))
        return list(self.predecessors(topic)) # Agreed interface from function
    
    def to_dict(self) -> dict:
        return nx.node_link_data(self, edges="edges")
