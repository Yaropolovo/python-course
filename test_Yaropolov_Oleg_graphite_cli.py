import pytest

from task_Yaropolov_Oleg_graphite_cli import process_parser_command

SAMPLE_INPUT = "wiki_search_app.log"
SAMPLE_INPUT_TRICKY = "wiki_search_app_tricky.log"
MY_LOCAL_HOST = "my_local_host"
MY_LOCAL_PORT = 1234

def test_correctly_calculate_both_required_metric(capsys):
    process_parser_command(SAMPLE_INPUT, "localhost", 2003)
    captured = capsys.readouterr()
    assert 80 == len(captured.out.split('\n')) - 1
    assert any('echo "wiki_search.article_found 28' in l for l in captured.out.split('\n'))
    assert any('echo "wiki_search.complexity 0.918' in l for l in captured.out.split('\n'))

# def test_correctly_calculate_metrics_for_tricky_queries(capsys):
#     process_parser_command(SAMPLE_INPUT_TRICKY, MY_LOCAL_HOST, MY_LOCAL_PORT)
#     captured = capsys.readouterr().out.split('\n')[:-1]
#     assert 8 == len(captured)
#     assert all(MY_LOCAL_HOST in captured)
#     assert all(str(MY_LOCAL_PORT) in captured)
#     assert 'wiki_search.complexity 0.655' in captured
#     assert 'wiki_search.complexity 86400.655' in captured
#     assert 'wiki_search.complexity 0.925' in captured
#     assert 'wiki_search.complexity 2.4' in captured

