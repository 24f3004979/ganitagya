from mool.tree import *

t = TopicGraph()

topics = [
        'Arithmatic',
        'Variables',
        'Equations',
        'Expressions',
'Simplification'
        ]

for i in topics:
    t.add_topic(i)

# dependency check
t.add_dependency('Variables', 'Equations')

d = t.downgrade_topic('Equations')

print(f"Downgrade response : {d}")

# Final dictionary view of the given unit
print(t.to_dict)
