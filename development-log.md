# Development Log book
Daily work log, project trace and progress tracks milestones and discussion topics during development, documenting build with simple documentation way.

[30-8-2026]
- Siddhi core data flow research
    As i kept into discussion about core data flow and expectation of module
    Some real hard problems
    1. Maping options of question towards topic dependency
    2. Error tracer engine for topic dependency tracing
    3. Question generation and modeling
    4. Comprehensive question modeling topic is really hard to tackle

- Cognitive problem solving research domains were hited during exploration of these problem and possible solution, currently only solution is to hard code everything into a data structure and wrap it into function
- Interesting areas for research and experiment, Modeling for problems options error tracing into programatical and matematical framework for proper solution tracing.
- dedicated model training pipeline with information from above designed data pipeline could benifit research into makng discriminative modeling for such questions

- Must require foundational data flow structure

[31-8-2026]

I am complicating things before it have started, thinking about initial design in good but things are geting over complicated then the scale i am really ment to be handeled, Thus i am going to make final concreet documentation and action plan for the whole project into one shot
    Making sepration about core must required features
    inhancements
    core logic flow for the application
    All must requirements for the Initial Project rollup

- Documenting concreet documentation as final decision for the project working state

[01-09-2026]

+ Initiated basic working root node first primitive version
+ Curating foundational mechanism for siddhi question module service
    This requires curated question generator
    for question generator we would need question template
   
[02-09-2026]
+ Siddhi Question template initiated
+ Prashna - Question generator with template engine working *tested
+ Prashna is completly working unit with inbuilt prashna generators making questions for all range with template render

We need now curated quiz handler backend service unit
    Handling generators,  response based topic node traversal and taking the question state into percistency
    We can have both levels one adaptive to user shot | other straight curated 10 questions for given topic range

+ Made foundational quiz handle object with 3 simple rules for topic update
    Making simple handle for question generation
+ Siddhi engine would only work to generate question
    separate quiz handle specified to generating questions tracking status and updates would be created along with global student handler obeject for student response handling unit
+ Engine Due for tommorow 
