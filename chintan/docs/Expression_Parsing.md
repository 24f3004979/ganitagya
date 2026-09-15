# Expression Parsing

A simple root utility for simplification of understand mathematical expressions and equation from numerical lense, making simplification through step by step break down of expression into simple component, easy for learner to understand how expression are solved and comprihended, 

**Tool would be later used for analysis of formulas, understanding formulas with numerical intuition helped with this tool plugged with ganitagya mitra** - Future References for project

## Concept Logic

Parsing Expression with precedence through left to right, where we take division and multiplication in same level of priority based on occurance in expression order.

## Implementation Logic

1. Iterate expression from left to right
2. components extraction
    + Groups with brackets for priority
    + Occurence based bundels of operation component
        List into component listing
        with each component based on occurence
