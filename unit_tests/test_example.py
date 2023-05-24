"""
An example script showing Pytest capabilities.

Using:
Create test files for your scripts you wish to test and
'assert' a known correct output for a given output to test your methods.

Settings:
pytest.ini in the root folder is responsible for managing how pytest runs.
pytest will currently test the 'unit_tests' folder.

Gotchas:
All test methods and scripts must start with 'test_'.
unit_tests must contain an '__init__.py'.
"""

def example_function(a_number:int) -> int:
    """ An example function that takes returns a given number incremented by one. """
    return a_number + 1

def test_1():
    """ An example test function that will PASS. """
    assert example_function(4) == 5

def test_2():
    """ An example test function that will FAIL. """
    assert example_function(4) == 6
