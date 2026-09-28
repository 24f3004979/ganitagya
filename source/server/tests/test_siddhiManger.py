from server.service.SiddhiManager import SiddhiUnit


unit = SiddhiUnit(1, 'Basic Arithmetic')

def test_generation():
    response = unit.generation(1)
    print(f"Generated response List : {response}")
    assert len(response) == 2

def test_evaluation():
    resp =  unit.evaluation([80,90])
    assert type(resp) == int

    
