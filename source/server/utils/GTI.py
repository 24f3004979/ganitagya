# GLOABL TOPIC INDEXING FILE
'''
Global topic indexing for referencing to build student knowledge graph and facilitate storage
intendted for first simplified version for student graph implementation | Future it would be moved into more evolved version with DB extractions

Indexing with simple topic listing into numerical encode and decode utility function
'''

topics = [
        "Basic Arithmetic",
        "Variable",
        "Expression",
        "Operation Order",
        "Simplification",
    ]

# Topic to number conversion

def encode(topic_name):
    '''
    With simplicity highly critical function use with intended 
    topic really exist with fail it would make problems
    '''
    if topic_name in topics:
        return topics.index(topic_name)  # Simply index number
    return None # topic not found

def decode(i:int):
    '''
    Simple index fetch from topic list
    '''
    if (i <= len(topics) - 1):
        return topics[i] # Simple index fetch