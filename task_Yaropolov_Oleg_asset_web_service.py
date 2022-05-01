#!/usr/bin/env python3
# from argparse import ArgumentParser, FileType
# import sys
import logging
import logging.config
from typing import Dict, List
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import requests
from flask import Flask, jsonify, request, abort


app = Flask(__name__)
# import yaml

WARN_PERIOD_THRESHOLD = 5
logger = logging.getLogger("asset")
CBR_DAILY_HTML = "https://www.cbr.ru/eng/currency_base/daily/"
CBR_KEY_INDICATOR_HTML = "https://www.cbr.ru/eng/key-indicators/"



@app.route("/cbr/daily")
def return_cbr_daily_jsonify():
    """"Jsonify response from CBR daily"""
    builded_dict = return_cbr_daily()
    return jsonify(builded_dict)
def return_cbr_daily():
    """get currency ratio from CBR website"""
    downloaded_text = download_cbr_daily()
    builded_dict = parse_cbr_currency_base_daily(downloaded_text)
    return builded_dict
def download_cbr_daily() -> str:
    """Wrapper for mocking"""
    downloaded_text = download_page_from_url(CBR_DAILY_HTML)
    return downloaded_text

@app.route("/cbr/key_indicators")
def return_cbr_key_indicators_jsonify():
    builded_dict = return_cbr_key_indicators()
    return jsonify(builded_dict)
def return_cbr_key_indicators():
    """get key indicators from CBR website"""
    builded_dict = parse_cbr_key_indicators(download_cbr_key_indicator())
    return builded_dict 
def download_cbr_key_indicator() -> str:
    """Wrapper for mocking"""
    downloaded_text = download_page_from_url(CBR_KEY_INDICATOR_HTML)
    return downloaded_text


@app.route("/api/asset/add/<string:char_code>/<string:name>/<capital>/<float:interest>")
def add_asset_from_web(char_code, name, capital, interest):
    """Add asset with provided parameters to the bank"""
    if ASSET_COLLECTION.asset_with_provided_name_is_already_exists(name):
        return f"Asset '{name}' is already exists!", 403
    ASSET_COLLECTION.add_by_params(name, float(capital), interest, char_code)
    return f"Asset '{name}' was successfully added", 200

@app.route("/api/asset/list")
def print_asset_collection():
    """Print json from all assets"""
    sorted_collection = ASSET_COLLECTION.return_to_request(None)
    return jsonify(sorted_collection), 200

@app.route("/api/asset/get")
def print_selected_asset():
    """Print json from required assets"""
    requested_assets = request.args.getlist("name")
    sorted_collection = ASSET_COLLECTION.return_to_request(requested_assets)
    return jsonify(sorted_collection), 200

@app.route("/api/asset/calculate_revenue")
def calculate_revenue_for_period():
    """Return revenue in json format"""
    requested_periods = request.args.getlist("period")
    daily_rate = return_cbr_daily()
    key_indicators = return_cbr_key_indicators()

    def exchange_rate(char_code: str) -> float:
        if "RUB" == char_code:
            return 1
        if char_code in key_indicators:
            return key_indicators[char_code]
        if char_code in daily_rate:
            return daily_rate[char_code]
        abort(501)

    revenues_for_period = {}

    for period in requested_periods:
        precise_answer = sum(asset.calculate_revenue(float(period))
                             * exchange_rate(asset.char_code)
                             for asset in ASSET_COLLECTION._asset_collection)
        revenues_for_period[period] = round(precise_answer, 8)
    return jsonify(revenues_for_period), 200

@app.route("/api/asset/cleanup")
def clear_asset_collection():
    """Drop all assets"""
    ASSET_COLLECTION.remove_all()
    return "there are no more assets", 200

@app.errorhandler(404)
def page_not_found(error):
    """The main page of the service"""
    return "This route is not found", 404

@app.errorhandler(503)
def CBR_is_not_available(error):
    """Page for missing pages"""
    return "CBR service is unavailable", 503

@app.errorhandler(501)
def Currency_is_not_available(error):
    """Page for missing currency"""
    return "Your currency is unavailable", 501

def download_page_from_url(url: str) -> str:
    '''Download page and return html as text'''
    # from pdb import set_trace; set_trace()
    # if not response.ok: # Тут нужно отлавливать только определенные ошибки
    #     abort(503)
    try:
        response = requests.get(url)
        return response.text
    except requests.exceptions.ConnectionError:
        abort(503)

def parse_cbr_currency_base_daily(html_data: str) -> Dict[str, float]:
    """Parse currency from text"""
    soup = BeautifulSoup(html_data, features="html.parser")
    return dict((tr.contents[3].contents[0], float(tr.contents[9].contents[0]) /
                 float(tr.contents[5].contents[0])) for
                tr in soup.find_all("tr")[1:])

def parse_cbr_key_indicators(html_data: str) -> Dict[str, float]:
    """Parse key_indicators from text"""
    soup = BeautifulSoup(html_data, features="html.parser")
    asset_dict = {}
    div_collection = soup.find_all("div", class_="table key-indicator_table")
    for div in div_collection[0:2]:
        asset_collection = div.find_all("tr")
        for asset in asset_collection[1:]:
            char_code = asset.find_all("td")[0].find_all("div")[2].contents[0]
            rate = float(asset.find_all("td")[-1].contents[0].replace(",", ""))
            asset_dict[char_code] = rate
    return asset_dict


class Component(ABC):
    """Composite pattern interface"""
    @abstractmethod
    def return_to_request(self):
        """Abstract method for printing assets"""

class Composite(Component):
    """Parent object of composite pattern"""
    def __init__(self) -> None:
        self._asset_collection: List[Component] = []

    def add(self, component: Component) -> None:
        """Add one asset"""
        self._asset_collection.append(component)

    def add_by_params(self, name: str, capital: float,
                      interest: float, char_code: str = "RUB") -> None:
        """Build and add asset"""
        asset = Asset(name, capital, interest, char_code)
        self.add(asset)

    # def remove(self, component: Component) -> None:
    #     """Remove one asset"""
    #     self._asset_collection.remove(component)

    def remove_all(self) -> None:
        """Clear collection"""
        for asset in self._asset_collection:
            self._asset_collection.remove(asset)

    def asset_with_provided_name_is_already_exists(self, name: str) -> bool:
        """Check whether asset exists"""
        return any(name == asset.name for asset in self._asset_collection)

    def return_to_request(self, required_assets) -> str:
        """Build ordered list from asset collection"""
        if required_assets:
            asset_collection = [asset.return_to_request() for asset in self._asset_collection if
                                asset.name in required_assets]
        else:
            asset_collection = [asset.return_to_request() for asset in self._asset_collection]

        def sort_by_char_code(list_input):
            """Sort by char_code"""
            return list_input[0]
        def sort_by_name(list_input):
            """Sort by name"""
            return list_input[1]
        def sort_by_capital(list_input):
            """Sort by capital"""
            return list_input[2]
        def sort_by_interest(list_input):
            """Sort by interest"""
            return list_input[3]

        return sorted(
            sorted(
                sorted(
                    sorted(asset_collection,
                           key=sort_by_interest),
                    key=sort_by_capital),
                key=sort_by_name),
            key=sort_by_char_code)

ASSET_COLLECTION = Composite()

class Asset(Component):
    """Leaf object of Composite pattern"""
    def __init__(self, name: str, capital: float, interest: float, char_code: str = "RUB"):
        self.name = name
        self.capital = capital
        self.interest = interest
        self.char_code = char_code

    def return_to_request(self):
        """Realization of abstract method"""
        return [self.char_code, self.name, self.capital, self.interest]

    def calculate_revenue(self, years: int) -> float:
        """Calculate profit for several years"""
        revenue = self.capital * ((1.0 + self.interest) ** years - 1.0)
        return revenue

    # @classmethod
    # def build_from_str(cls, raw: str):
    #     logger.debug("building asset object...")
    #     name, capital, interest = raw.strip().split()
    #     capital = float(capital)
    #     interest = float(interest)
    #     asset = cls(name=name, capital=capital, interest=interest)
    #     return asset

    def __repr__(self):
        repr_ = f"{self.__class__.__name__}({self.name}, {self.capital}, {self.interest})"
        return repr_

    def __eq__(self, rhs):
        outcome = (
            self.name == rhs.name
            and self.capital == rhs.capital
            and self.interest == rhs.interest
        )
        return outcome


# def load_asset_from_file(fileio):
#     logger.info("reading asset file...")
#     raw = fileio.read()
#     asset = Asset.build_from_str(raw)
#     return asset


# def process_cli_arguments(arguments):
#     print_asset_revenue(arguments.asset_fin, arguments.periods)
#
# def print_asset_revenue(asset_fin, periods):
#     asset = load_asset_from_file(asset_fin)
#     if len(periods) >= WARN_PERIOD_THRESHOLD:
#         logger.warning("too many periods were provided: %s", len(periods))
#     for period in periods:
#         revenue = asset.calculate_revenue(period)
#         logger.debug("asset %s for period %s gives %s", asset, period, revenue)
#         print(f"{period:5}: {revenue:10.3f}")

# def setup_logging(logging_yaml_config_fpath):
#     """setup logging via YAML if it is provided"""
#     if logging_yaml_config_fpath:
#         with open(logging_yaml_config_fpath) as config_fin:
#             logging.config.dictConfig(yaml.safe_load(config_fin))


# def setup_parser(parser):
#     parser.add_argument("-f", "--filepath", dest="asset_fin", default=sys.stdin, type=FileType("r"))
#     parser.add_argument("-p", "--periods", nargs="+", type=int, metavar="YEARS", required=True)
#     parser.add_argument(
#         "--logging-config", dest="logging_yaml_config_fpath",
#         default=None, help="path to logging config in YAML format",
#     )
#     parser.set_defaults(callback=process_cli_arguments)


# def main():
#     parser = ArgumentParser(
#         prog="asset",
#         description="tool to forecast asset revenue",
#     )
#     setup_parser(parser)
#     arguments = parser.parse_args()
#     setup_logging(arguments.logging_yaml_config_fpath)
#     arguments.callback(arguments)
#
#
# if __name__ == "__main__":
#     main()
