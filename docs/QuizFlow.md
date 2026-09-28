# Siddhi Engine based Quiz Engine

AIM : Adaptive quesions engine

## Flow 

1. Select Questions Number, topic selection
2. question generation
3. Evaluation Loop
  
  Main Core of Managing with siddhi Module

Current version would store info into temporary memory
DB based edits would be taken through topic changing report generation sequence


  check answers -> adjust engine parameter
  Simple Conditions
  + 2 wrong -> downgrade topic -> Append for topics to learn listing | update topic level to 1
    topics to work into : which got into changing
  + 1 right | 1 wrong -> keep same level
    difficulty faced questions
  + both right | increase level for question with adding current level to student reference
    Add that topic for strong topic listing

  Generating final report
  - changed topics listing
  - topics with difficulty faced listing
  - Acced topic listing

4. Report Generation

  + Iterating topics and making changes to the DB student relation with topics
  + Changing levels to reflect at student dashboard


