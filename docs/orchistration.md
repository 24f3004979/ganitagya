# Orchistration Layer 

Siddhi unit working with student db layer for managing quiz state and final wrapping api endpoint designs,
questions generated needs to be stored for references through siddhi manager engine

With dedicated utility for questions storage into simple sheet for references for student quiz management
keeping simple flow for quiz and its results along with sync of final edits generation reports.

Doc contains : simple plans about stateless upgrade for evaluation and generation trip to server through user response

## Simple Ideation phased design flow

```

current situation
It does changes student DB state with its hit -> No question persistency recorded
generates question for new refresh with lost data about prev questions

Core components
1. Generation Unit
  + generating questions
  + Engine Level Adjustment
  + Student Level fetched based update but Memory based

2. Evaluation 
  + Works in memory to check about answers
  + Matches user response with internal indexed questions
  + In memory dependency for checking answers
```

Upgrade Required
DB connection for question dump and load during evaluation round to server required for improvement
upong surviving reload | conflicting crashes

+ Dumping generated questions with quiz id to DB
+ Making dedicated component to work with questions generation and DB layer sync
 
