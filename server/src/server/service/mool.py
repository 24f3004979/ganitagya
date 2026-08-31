'''
Root Information repository instance

    + topic traversal
    + building root node tree
'''
from networkx import DiGraph

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