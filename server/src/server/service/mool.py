'''
Root Information repository instance

    + topic traversal
    + building root node tree
'''
from networkx import DiGraph
import networkx as nx
import matplotlib.pyplot as plt

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

    def draw(self):
        '''
        Consistent Image for the graph visualization
        '''
        pos = nx.spring_layout(self, seed=42, center=(0,0))  # seed keeps the layout consistent

        plt.figure(figsize=(14, 10))  # Set canvas size

        nx.draw(
            self,
            pos,
            with_labels=True,  # Show node names
            node_color="skyblue",  # Node background color
            node_size=1200,  # Size of nodes
            node_shape="o",  # 'o' = circle, 's' = square, etc.
            font_size=12,  # Node label font size
            font_weight="bold",  # Font weight
            font_color="darkblue",  # Font color
            edge_color="gray",  # Color of the lines
            width=2,  # Line width of the edges
            arrowsize=20,  # Size of direction arrows (for DiGraph)
            connectionstyle="arc3,rad=0.1",  # Slightly curve the edges
        )

        plt.title("Concept Graph", fontsize=16)
        plt.show()


