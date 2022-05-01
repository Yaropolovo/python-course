#!/usr/bin/env python3
from argparse import ArgumentParser, FileType
import logging
import logging.config
import sys

import yaml

WARN_PERIOD_THRESHOLD = 5
APPLICATION_NAME = 'asset'
logger = logging.getLogger(APPLICATION_NAME)
LOGGER_WARNING_NAME = 'asset_log.warn'
LOGGER_DEBUG_NAME = 'asset_log.debug'
LOGGER_CONF_YAML_PATH = 'task_Yaropolov_Oleg_asset_log.conf.yml'

class Asset:
    def __init__(self, name: str, capital: float, interest: float):
        self.name = name
        self.capital = capital
        self.interest = interest

    def calculate_revenue(self, years: int) -> float:
        revenue = self.capital * ((1.0 + self.interest) ** years - 1.0)
        return revenue

    @classmethod
    def build_from_str(cls, raw: str):
        logger.debug("building asset object...")
        name, capital, interest = raw.strip().split()
        capital = float(capital)
        interest = float(interest)
        asset = cls(name=name, capital=capital, interest=interest)
        return asset

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



def load_asset_from_file(fileio):
    logger.info("reading asset file...")
    raw = fileio.read()
    asset = Asset.build_from_str(raw)
    return asset


def process_cli_arguments(arguments):
    print_asset_revenue(arguments.asset_fin, arguments.periods)


def print_asset_revenue(asset_fin, periods):
    asset = load_asset_from_file(asset_fin)

    if len(periods) >= WARN_PERIOD_THRESHOLD:
        logger.warning("too many periods were provided: %s", len(periods))

    for period in periods:
        revenue = asset.calculate_revenue(period)
        logger.debug("asset %s for period %s gives %s", asset, period, revenue)
        print(f"{period:5}: {revenue:10.3f}")


def setup_logging(logging_yaml_config_fpath):
    """setup logging via YAML if it is provided"""
    # if logging_yaml_config_fpath:
    #     with open(logging_yaml_config_fpath) as config_fin:
    #         logging.config.dictConfig(yaml.safe_load(config_fin))
            # from pdb import set_trace; set_trace()
    
    logger = logging.getLogger(APPLICATION_NAME)
    # logging.basicConfig(
    #     stream = sys.stderr,
    #     level = logging.DEBUG,
    #     filename = 'asset.log',
    # )

    simple_formatter = logging.Formatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # debug_file_handler = logging.FileHandler(
    #     filename = LOGGER_DEBUG_NAME,
    #     mode = 'r',
    # )
    # debug_file_handler.setLevel(logging.DEBUG)
    # debug_file_handler.setFormatter(simple_formatter)
    #
    warning_file_handler = logging.FileHandler(
        filename = LOGGER_WARNING_NAME,
        # mode = 'r+',
    )
    warning_file_handler.setLevel(logging.WARNING)
    warning_file_handler.setFormatter(simple_formatter)

    info_err_handler = logging.StreamHandler(sys.stderr) #the same as stream=sys.stderr
    info_err_handler.setLevel(logging.INFO)
    info_err_handler.setFormatter(simple_formatter)

    logger = logging.getLogger(APPLICATION_NAME)
    logger.setLevel(logging.DEBUG)
    # logger.addHandler(debug_file_handler)
    logger.addHandler(warning_file_handler)
    logger.addHandler(info_err_handler)
    
    # logger = logging.getLogger()
    # logger.addHandler(file_handler)

def setup_parser(parser):
    parser.add_argument("-f", "--filepath", dest="asset_fin", default=sys.stdin, type=FileType("r"))
    parser.add_argument("-p", "--periods", nargs="+", type=int, metavar="YEARS", required=True)
    parser.add_argument(
        "--logging-config", dest="logging_yaml_config_fpath",
        default=LOGGER_CONF_YAML_PATH, help="path to logging config in YAML format",
    )
    parser.set_defaults(callback=process_cli_arguments)


def main():
    parser = ArgumentParser(
        prog="asset",
        description="tool to forecast asset revenue",
    )
    setup_parser(parser)
    arguments = parser.parse_args()
    setup_logging(arguments.logging_yaml_config_fpath)
    arguments.callback(arguments)


if __name__ == "__main__":
    main()

