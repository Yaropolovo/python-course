import pytest

from task_Yaropolov_Oleg_repeater import verbose, repeater, verbose_context

INT_FOR_REPETITION = 3

def test_verbose_with_arguments(capsys):
    @verbose
    def hello(name: str) -> None:
        print(f'Hello {name}')

    hello("Oleg")
    outcome = capsys.readouterr().out.split('\n')
    assert 4 == len(outcome)
    assert "before function call" == outcome[0]
    assert "Hello Oleg" == outcome[1]
    assert "after function call" == outcome[2]

def test_repeater_with_argumnets(capsys):
    @repeater(count=INT_FOR_REPETITION)
    def hello(name:str) -> None:
        print(f'Hello {name}')

    hello("Oleg")
    outcome = capsys.readouterr().out.split('\n')
    assert INT_FOR_REPETITION + 1 == len(outcome)
    assert "Hello Oleg" == outcome[0]

def test_verbose_context_as_decorator(capsys):
    @verbose_context()
    def hello(name: str) -> None:
        print(f'Hello {name}')

    hello("Oleg")
    outcome = capsys.readouterr().out.split('\n')
    assert 4 == len(outcome)
    assert "class: before function call" == outcome[0]
    assert "Hello Oleg" == outcome[1]
    assert "class: after function call" == outcome[2]

def test_verbose_context_as_context(capsys):
    with verbose_context():
        print("Hello Oleg")

    outcome = capsys.readouterr().out.split('\n')
    assert 4 == len(outcome)
    assert "class: before function call" == outcome[0]
    assert "Hello Oleg" == outcome[1]
    assert "class: after function call" == outcome[2]

    # from pdb import set_trace; set_trace()
