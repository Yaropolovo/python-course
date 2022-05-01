import requests
import logging.config
import yaml
# import sys

from lxml import etree
from flask import Flask, request, abort, jsonify

app = Flask(__name__)
WIKI_BASE_URL = "https://en.wikipedia.org"
WIkI_BASE_SEARCH_URL = f"{WIKI_BASE_URL}/w/index.php?search="
QUERIES_COLLECTION_LOCAL = "wikipedia_search_queries.txt"

logging.config.dictConfig(yaml.safe_load("""
version: 1
formatters: 
    simple:
        format: "%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s"
        datefmt: "%Y%m%d_%H%M%S"
handlers: 
    stream_handler: 
        class: logging.StreamHandler
        stream: ext://sys.stderr
        level: DEBUG
        formatter: simple
    file_handler:
        class: logging.FileHandler
        filename: wiki_search_app.log
        level: DEBUG
        formatter: simple
loggers:
    werkzeug:
        level: DEBUG
        propagate: False
        handlers:
            - stream_handler
root:
    level: DEBUG
    handlers:
        - stream_handler
"""))

@app.errorhandler(404)
def page_not_found(error):
    """The main page of the service"""
    return "This route is not found", 404

@app.errorhandler(503)
def wiki_is_not_available(error):
    """Page for missing pages"""
    return "Wikipedia Search Engine is unavailable", 503

def download_page_from_url(url: str):
    '''Download page and return html as text'''
    try:
        response = requests.get(url)
        return response.text, response.status_code
    except requests.exceptions.ConnectionError:
        abort(503)

@app.route("/search")
def wiki_proxy_search():
    """search realization"""
    user_query = request.args.get("query")
    wiki_response_text, wiki_response_status = \
        download_page_from_url(WIkI_BASE_SEARCH_URL + user_query)
    return wiki_response_text, wiki_response_status

# @app.route("/search_all")
# def api_search_predifined_list_of_queris():
#     with open(QUERIES_COLLECTION_LOCAL) as fin:
#         queries_collection = fin.read()
#     for query in queries_collection.split("\n")[:-1]:
#         # app_response = client.get("/api/search?query="+query)
#         # user_query = request.args.get("query")
#         app.logger.debug("start processing query: %s", query)
#         # print("special message to console", file=sys.stderr)
#         wiki_response = requests.get(WIkI_BASE_SEARCH_URL + query)
#         if not wiki_response.ok:
#             abort(503)
#         article_count = count_wiki_search_output(wiki_response.text)
#         app.logger.info("found %s articles for query: %s", article_count, query)
#         app.logger.debug("finish processing query: %s", query)
#     return "Done!", 200

@app.route("/api/search")
def api_wiki_proxy_search():
    """route for article_count calculation"""
    user_query = request.args.get("query")
    app.logger.debug("start processing query: %s", user_query)
    wiki_response_text, wiki_response_status = \
        download_page_from_url(WIkI_BASE_SEARCH_URL + user_query)
    # wiki_response = requests.get(WIkI_BASE_SEARCH_URL + user_query)
    article_count = count_wiki_search_output(wiki_response_text)
    app.logger.info("found %s articles for query: %s", article_count, user_query)
    app.logger.debug("finish processing query: %s", user_query)
    return jsonify({
        "version": 1.0,
        "article_count": article_count,
    })

def count_wiki_search_output(wiki_search_output_html):
    """count results"""
    root = etree.fromstring(wiki_search_output_html, etree.HTMLParser())
    try:
        article_count = root.xpath(".//div[@class='results-info']/@data-mw-num-results-total")[0]
    except IndexError:
        article_count = 0
    return int(article_count)

def parse_wiki_search_output(wiki_search_output_html):
    """parsing html"""
    root = etree.fromstring(wiki_search_output_html, etree.HTMLParser())
    documents = root.xpath("//li[@class='mw-search-result']")
    document_collection = []
    for document in documents:
        title = document.xpath(".//a[1]/@title")[0]
        link = document.xpath(".//a[1]/@href")[0]
        snippet = "".join(document.xpath(".//div[@class='searchresult']")[0].itertext())
        document_collection.append([title, link, snippet,])
    return document_collection
