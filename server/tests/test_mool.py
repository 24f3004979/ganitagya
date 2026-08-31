from server.service import ConceptGraph
import matplotlib.pyplot as plt
import networkx as nx

def test_mool():
    g = ConceptGraph()
    r = g.add_concept('Algebra')

    print(g)
    nx.draw(g, with_labels=True)
    plt.show()
    assert type(r) == type(r)