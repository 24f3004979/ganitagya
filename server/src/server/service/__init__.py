from .mool import ConceptGraph


# Root Graph Build
def build_root_concept_graph():
    graph = ConceptGraph()

    topics = [
        "Basic Arithmetic",
        "Variable",
        "Expression",
        "Operation Order",
        "Simplification",
    ]

    for topic in topics:
        graph.add_concept(topic)

    graph.add_dependencies(
        [
            "Basic Arithmetic",
            "Variable",
            "Expression",
            "Operation Order",
        ],
        "Simplification",
    )

    graph.add_dependencies(
        [
            "Basic Arithmetic",
            "Variable",
            "Expression",
        ],
        "Operation Order",
    )

    graph.add_dependencies(
        [
            "Basic Arithmetic",
            "Variable",
        ],
        "Expression",
    )

    graph.add_dependency(
        "Basic Arithmetic",
        "Variable",
    )

    return graph

RootConceptGraph = build_root_concept_graph()
