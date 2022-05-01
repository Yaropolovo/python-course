import logging
import pytest
from argparse import ArgumentParser, FileType

from asset import Asset, load_asset_from_file, print_asset_revenue, WARN_PERIOD_THRESHOLD, setup_parser
# from task_Yaropolov_Oleg_asset_log import Asset, load_asset_from_file, print_asset_revenue, WARN_PERIOD_THRESHOLD

# LOGGER_WARNING_NAME = 'asset_log.warn'
# LOGGER_DEBUG_NAME = 'asset_log.debug'
# LOGGER_CONF_YAML_PATH = 'task_Yaropolov_Oleg_asset_log.conf.yml'
ASSET_EXAMPLE_PATH = 'asset_example_generated.txt'


@pytest.fixture
def asset_example():
    return Asset('property', 1000, 0.1)

@pytest.fixture
def generated_asset_example(tmpdir, asset_example) -> str:
    with open(tmpdir.join(ASSET_EXAMPLE_PATH), 'w') as fo:
        fo.write(f'{asset_example.name}   {asset_example.capital}   {asset_example.interest}')
    return tmpdir.join(ASSET_EXAMPLE_PATH)


def test_asset_example_generation_is_correct(asset_example, generated_asset_example):
    with open(generated_asset_example) as fi:
        loaded_asset = load_asset_from_file(fi)
    assert asset_example == loaded_asset


def test_load_configuration_is_correct():
    parser = ArgumentParser(
        prog="asset",
        description="tool to forecast asset revenue",
    )
    setup_parser(parser)
    pass

@pytest.mark.parametrize(
    "periods", [
        pytest.param([1,3,5], id='a_few_periods'),
        pytest.param([1,2,3,4,5,6], id='too_many_periods'),
    ]
)
def test_logging_on_trivial_example(caplog, capsys, generated_asset_example, periods):
    caplog.set_level('DEBUG')
    with open(generated_asset_example) as fi:
        print_asset_revenue(generated_asset_example, periods)

    captured = capsys.readouterr()
    # from pdb import set_trace; set_trace()
    # with open(LOGGER_WARNING_NAME) as f_warn:
    #     log_warn_content = f_warn.read().strip().split('\n')
    # with open(LOGGER_DEBUG_NAME) as f_deb:
    #     log_deb_content = f_deb.read().strip().split('\n')

    assert len(periods) == len(captured.out.split('\n')) - 1
    assert '' == captured.err
    assert any('reading asset file' in message for message in caplog.messages)
    if len(periods) < WARN_PERIOD_THRESHOLD:
        assert any('building asset object' in message for message in caplog.messages)
        assert all(rec.levelno <= logging.WARNING for rec in caplog.records), (
            'Application is unstable, there are Warnings :('
        )
    else:
        assert any('too many periods' in message for message in caplog.messages)
        assert any(rec.levelno == logging.WARNING for rec in caplog.records)


