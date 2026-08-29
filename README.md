# Ganitagya
**A platform to learn discover and grow**

## Problem and scope of solution

Problem : Students struggle understanding math, either they rote learn things, or they just fear mathematics, questions makes more suffer with surprised abstract topics where student still lacks fundamental

### Critical Issues
1. Working on fundamental becomes just students responsibility and later builds fomo rather then encouragement to work  on those.
2. Separate concern with domains like geometry and number adds more complexity where as student should see them as one bloom of flowers.
3. Solving problem needs an approach where they can use what they know not just pluging formula and checking answers

### Proposed solution pathway

1. An Diagnostic error tracing question system which can adapt as per student attempt, degrade difficulty and switch to lower dependency questions to trace down exact topics which needs focus
    Helping student to identify where we would work together

2. Interface with both perspective support one with geometric view and one with numerical disection, giving student a whole approach towards problem from both lens

    + Numerical Disection tool
        Dedicated tool which can break Numerical equations and problem into steps
        make animated pathway to show case the approach with numeber blocks.

    + Graphing tool disection
        Graphs the equation into visual way.
        numerical way -> visual connection lens

3. Interactive environment with defined case study about domain which student loves, would interest more to student to learn new things and to approach to solve problem

4. Helping LLM [
    dedicated helper which can tweak the interactive environment to nudge student questions and hints
    integrated with platform with grounding information and elements control interface
]

5. Knowledge graph | gyan vriksha
    Repository of topics and information
        Used by all other elements to track student progress
        and give student visual feed back about his progress.

    nodes[topics] which student knows
    which topic student have choosed to work with
    what is going to be pathway for learning them

### CORE COMPONENT
1. Diagnostic Quiz Engine [ Siddhi ]
    Generates new questions with given sample template
    maps options to required topics
    analyses answering pattern and adapts difficulty

    final summary consists of error traced topics and whole analysis

2. Learning Interface | Chintan
    + Example walkthough <-- Used by LLM
    + Topics Equation disection
    + A tool student can also use to explore equations and expression

3. Helping LLM | Mitra
    + Hints and questions with respect to environment interaction of student
    + Controler Interface connection with interface manupulation