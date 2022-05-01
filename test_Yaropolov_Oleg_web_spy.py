from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import pytest
import requests
from bs4 import BeautifulSoup
from unittest.mock import patch

from task_Yaropolov_Oleg_web_spy import GITHUB_PRODUCTS_URL, calculate_products_from_url, callback_gitlab, setup_parser, Products
# GITLAB_DUMP_FILEPATH = "gitlab_features_expected.html"
GITLAB_DUMP_FILEPATH_FOR_TESTS = "gitlab_features.html"
GITLAB_DUMP_FILEPATH_EXPECTED = "gitlab_features_expected.html"

@pytest.fixture
def expected_numbers():
    '''Might be determined by stored file'''
    return [351,218]

@pytest.mark.slow
def test_parser_is_initialized_correctly():
    parser = ArgumentParser(
        prog="web_spy",
        description="the application for spying!"
    )
    setup_parser(parser)
    

@patch('task_Yaropolov_Oleg_web_spy.download_page_from_url')
@pytest.mark.slow
def test_check_output(mock_downloaded_page, capsys):
    mock_downloaded_page.return_value = open(GITLAB_DUMP_FILEPATH_FOR_TESTS, encoding="utf8").read()
    callback_gitlab(None)
    captured = capsys.readouterr()
    # from pdb import set_trace; set_trace()
    assert 'free' in captured.out
    assert 'enterprise' in captured.out

@patch('task_Yaropolov_Oleg_web_spy.download_page_from_url')
@pytest.mark.slow
def test_mocked_and_stored_numbers_are_the_same(mock_downloaded_page, expected_numbers):
    ''' Use local dump gitlab_features.html via mock '''
    mock_downloaded_page.return_value = open(GITLAB_DUMP_FILEPATH_FOR_TESTS, encoding="utf8").read()
    products = calculate_products_from_url(GITHUB_PRODUCTS_URL)
    downloaded_numbers = [products.free, products.enterprise]
    assert expected_numbers == downloaded_numbers, (
        f"expected free product count is {expected_numbers[0]}, while you calculated {downloaded_numbers[0]}; "
        f"expected enterprise product count is {expected_numbers[1]}, while you calculated {downloaded_numbers[1]}")

@pytest.mark.integration
def test_github_prod_request_is_successful():
    ''' Required internet '''
    response = requests.get(GITHUB_PRODUCTS_URL)
    assert bool(response)

@pytest.mark.integration
def test_downloaded_and_stored_numbers_are_the_same():
    '''
    This test should compare that number of products remains the same
    Should download the page and compare it with gitlab_features_expected.html
    '''
    products = calculate_products_from_url(GITHUB_PRODUCTS_URL)
    downloaded_numbers = [products.free, products.enterprise]

    expected_html_page = open(GITLAB_DUMP_FILEPATH_EXPECTED, encoding="utf8").read()
    soup = BeautifulSoup(expected_html_page, features="html.parser")
    expected_numbers = [len(soup.find_all(attrs = {"title": "Available in GitLab SaaS Free"})), \
                       len(soup.find_all(attrs = {"title": "Not available in SaaS Free"}))]
    
    assert expected_numbers == downloaded_numbers, (
        f"expected free product count is {expected_numbers[0]}, while you calculated {downloaded_numbers[0]}; "
        f"expected enterprise product count is {expected_numbers[1]}, while you calculated {downloaded_numbers[1]}")
    
    

