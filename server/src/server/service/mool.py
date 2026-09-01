'''
Root Information repository instance

    + topic traversal
    + building root node tree
'''
from networkx import DiGraph
import networkx as nx

from server.exceptions import DependencyClash
from server.dev_log import log

class ConceptGraph(DiGraph):
    '''
    Root concept graph for root information flow
    simple functional override for root information
    '''
    def add_concept(self, topic:str) -> "ConceptGraph":
        '''
        Adding topic into the main graph
        fall back requirement for rollback of addition
        '''
        self.add_node(topic)  # Topic added
        return self

    def add_dependency(self, prerequisite:str, topic:str) -> 'ConceptGraph':
        '''
        Topic dependency addition
        Fall back Error with circle dependency problem
        '''
        self.add_edge(prerequisite, topic)

        if not nx.is_directed_acyclic_graph(self):
            log.warning("Action Terminated for making cycle condition at root node")
            self.remove_edge(prerequisite, topic)  # Reverting changes
            raise DependencyClash(f'Addition of {prerequisite}->{topic} connection is making cycle')
        # Returning Object after check about dependency
        return self

    def add_dependencies(self, prerequisite_list:list[str], topic:str) -> 'ConceptGraph':
        for concept in prerequisite_list:
            self.add_dependency(concept, topic)
        return self

    def downgrade_concept(self, topic:str) -> list[str]:
        if self.in_degree(topic) == 0:
            log.info(f'Target Node :{topic} is super parent root')
            return [] # Root Node query
        return list(self.predecessors(topic))

    def upgrade_concept(self, topic:str) -> list[str]:
        if self.out_degree(topic) == 0:
            log.info(f"Target Node : {topic} is leaf node with no branches")
            return []
        return list(self.successors(topic))
