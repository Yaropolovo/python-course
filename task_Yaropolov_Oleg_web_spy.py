import sys

from argparse import ArgumentParser
import requests
from bs4 import BeautifulSoup

GITHUB_PRODUCTS_URL = 'https://about.gitlab.com/features/'

class Products:
    '''Class to store number of products'''
    def __init__(self, free: int, enterprise: int):
        self.free = free
        self.enterprise = enterprise

def download_page_from_url(url: str) -> str:
    '''Download page and return html as text'''
    response = requests.get(url)
    return response.text

def calculate_products_from_url(url: str) -> Products:
    '''Calculate free and enterprise number of products'''
    response_text = download_page_from_url(url)
    soup = BeautifulSoup(response_text, features="html.parser")

    free_products_num = len(soup.find_all(attrs={"title":"Available in GitLab SaaS Free"}))
    enterprise_products_num = len(soup.find_all(attrs={"title":"Not available in SaaS Free"}))
    products = Products(free_products_num, enterprise_products_num)

    return products

def procces_gitlab_arguments():
    '''Procces arguments from parser CLI'''
    products = calculate_products_from_url(GITHUB_PRODUCTS_URL)
    print(f"free products: {products.free}", file=sys.stdout)
    print(f"enterprise products: {products.enterprise}", file=sys.stdout)


def callback_gitlab(arguments):
    '''Execute gitlab command from CLI'''
    procces_gitlab_arguments()

def setup_parser(parser: ArgumentParser) -> None:
    """Determine the set of parameters for CLI"""
    subparsers = parser.add_subparsers(help="choose source")

    gitlab_parser = subparsers.add_parser(
        "gitlab",
        help="Check url: https://about.gitlab.com/features/",
    )
    gitlab_parser.set_defaults(callback=callback_gitlab)

def main():
    '''Init CLI and execute commands'''
    parser = ArgumentParser(
        prog="web_spy",
        description="the application for spying!"
    )
    setup_parser(parser)
    arguments = parser.parse_args()
    arguments.callback(arguments)


if __name__ == "__main__":
    main()

