from server.service import ConceptGraph
import matplotlib.pyplot as plt
import networkx as nx
import pytest

from server.exceptions import *
from server.dev_log import log

# Global Single object for testing
g = ConceptGraph()

topics = [
        "Arithmatic",
        "Variables",
        "Expression",
        "Order of Operation",
        "Simplification"
        ]

def visualize(): 
    nx.draw(g, with_labels=True)
    plt.show()



def test_mool_root_addition():
    '''
    Testing Concept addition node
    '''
    for _ in topics:
        g.add_concept(_)  # new topic

    assert len(g) == 5 # length value should match expection


# Cyclic dependency check testing
def test_cycle_dependency():
    '''
    Testing cyclic dependency fall back and response behaviour
    '''
    g.add_dependency('Arithmatic', 'Order of Operation')
    visualize()

    with pytest.raises(DependencyClash):
        g.add_dependency('Order of Operation', 'Arithmatic')

def test_load_dependency():
    dependency = [
            'Order of Operation',
            'Variables',
            'Arithmatic'
            ]
    g.add_dependencies(dependency, 'Simplification')
    visualize()

def test_upgrade():
    topic = g.upgrade_concept('Order of Operation')
    log.info(f"Topic upgrade listing : {topic}")
    assert topic[0] == 'Simplification'

def test_downgrade():
    topic = g.downgrade_concept('Simplification')
    log.info(f'testing : {topic} <- response from downgradig concept')
    assert topic == ['Order of Operation', 'Variables', 'Arithmatic']

# Downgrade exception load
def test_exc_upgrading():
    t = g.upgrade_concept('Simplification')
    assert t == []

def test_exc_downgrade():
    t = g.downgrade_concept('Arithmatic')
    assert t == []
