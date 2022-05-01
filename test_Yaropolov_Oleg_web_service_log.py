import pytest
from unittest.mock import patch

from task_Yaropolov_Oleg_web_service_log import app, parse_wiki_search_output

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

LOCAL_WIKI_HTML = "wikipedia_python_network.html"
LOCAL_WIKI_EMPTY_HTML = "wikipedia_redlockfifo_test.html"
# QUERIES_COLLECTION_LOCAL = "wikipedia_search_queries.txt"
# STORAGE_FOR_LOG = "wiki_search_app.log"
FIRST_PYTHON_NETWORK_RESULT = [
    "Python (programming language)",
    "/wiki/Python_(programming_language)",
    "Python is an interpreted high-level general-purpose programming language. Its design philosophy emphasizes code readability with its use of significant"
]

@patch("task_Yaropolov_Oleg_web_service_log.download_page_from_url")
def test_can_proxy_request_to_wiki(mock_wiki, client):
    mock_wiki.return_value = open(LOCAL_WIKI_HTML, encoding="utf8").read(), 200
    app_response = client.get("/search?query=python network")
    # from pdb import set_trace; set_trace()
    # assert 200 ==  app_response.status_code
    assert "NetworkX" in app_response.data.decode(app_response.charset)

# def test_can_proxy_request_to_wiki_and_get_json_output(client):
#     app_response = client.get("/api/search?query=python network")
#     assert 200 ==  app_response.status_code
#     assert app_response.is_json
#     json_response = app_response.get_json()
#     assert 20 == len(json_response["documents"])
#     assert FIRST_PYTHON_NETWORK_RESULT == json_response["documents"][0]
#     assert any("NetworkX" in document[2] for document in json_response["documents"])

@patch("task_Yaropolov_Oleg_web_service_log.download_page_from_url")
def test_can_calculate_article_count(mock_wiki, client):
    mock_wiki.return_value = open(LOCAL_WIKI_HTML, encoding="utf8").read(), 200
    app_response = client.get("/api/search?query=python network")
    # assert 200 ==  app_response.status_code
    assert app_response.is_json
    json_response = app_response.get_json()
    assert 3236 == json_response["article_count"]
    mock_wiki.return_value = open(LOCAL_WIKI_EMPTY_HTML, encoding="utf8").read(), 200
    app_response = client.get("/api/search?query=python redlockfifo test")
    assert 3236 == json_response["article_count"]


def test_can_parse_wiki_search_output():
    with open(LOCAL_WIKI_HTML) as fin:
        wiki_search_output_html = fin.read()
    documents = parse_wiki_search_output(wiki_search_output_html)
    assert 20 == len(documents)
    assert FIRST_PYTHON_NETWORK_RESULT == documents[0]

def test_errors(client):
    # with pytest.raises():
    app_response = client.get("/this_route_does_not_exists")
    assert 404 == app_response.status_code
    assert "This route is not found" == app_response.data.decode(app_response.charset)
# def test_make_queries_and_store_log(client, capsys):
#     with open(QUERIES_COLLECTION_LOCAL) as fin:
#         queries_collection = fin.read()
# 
#     for query in queries_collection.split("\n")[:-1]:
#         app_response = client.get("/api/search?query="+query)
    #     captured = capsys.readouterr().err
    #     from pdb import set_trace; set_trace()
    # 
    # 
    # with open(STORAGE_FOR_LOG) as fout:
    #     fout.write(captured)
