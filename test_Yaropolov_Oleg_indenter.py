import pytest

# from task_Yaropolov_Oleg_indenter import Indenter
from task_kolchanov_anton_indenter import Indenter

def test_indenter_1(capsys):
    with Indenter() as indent:
        indent.print("hi")
        with indent:
            indent.print("hello")
            with indent:
                indent.print("bonjour")
        indent.print("hey")
    outcome = capsys.readouterr().out
    # from pdb import set_trace; set_trace()

    assert "hi\n    hello\n        bonjour\nhey\n" == outcome

def test_indenter_2(capsys):
    with Indenter(indent_str="--") as indent:
        indent.print("hi")
        with indent:
            indent.print("hello")
            with indent:
                indent.print("bonjour")
        indent.print("hey")
    outcome = capsys.readouterr().out
    assert "hi\n--hello\n----bonjour\nhey\n" == outcome

def test_indenter_3(capsys):
    with Indenter(indent_str="--", indent_level=1) as indent:
        indent.print("hi")
        with indent:
            indent.print("hello")
            with indent:
                indent.print("bonjour")
        indent.print("hey")
    outcome = capsys.readouterr().out
    from pdb import set_trace;     set_trace()
    assert "--hi\n----hello\n------bonjour\n--hey\n" == outcome
## Написать тесты с другими параметрами indenter
