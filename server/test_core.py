from src.server.service.mool import *

def test_core():
    r = core_function()
    assert r == 1
