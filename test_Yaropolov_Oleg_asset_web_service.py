import pytest
from unittest.mock import patch
# from bs4 import BeautifulSoup

from task_Yaropolov_Oleg_asset_web_service import parse_cbr_currency_base_daily, parse_cbr_key_indicators, ASSET_COLLECTION, return_cbr_daily, return_cbr_key_indicators
from task_Yaropolov_Oleg_asset_web_service import app as tested_app

# from pdb import set_trace; set_trace()

@pytest.fixture
def client():
    with tested_app.test_client() as client:
        yield client

CBR_CURRENCY_DAILY_LOCAL = "cbr_currency_base_daily.html"
CBR_KEY_INDICATOR_LOCAL = "cbr_key_indicators.html"

def test_daily_parsing_is_correct():
    parsed_currency_collection = parse_cbr_currency_base_daily(open(CBR_CURRENCY_DAILY_LOCAL, encoding="utf8").read())
    assert 0.144485 == parsed_currency_collection["AMD"]
    assert 5.169 == parsed_currency_collection["ZAR"]

def test_key_indicator_parsing_is_correct():
    parsed_key_indicator_collection = parse_cbr_key_indicators(open(CBR_KEY_INDICATOR_LOCAL, encoding="utf8").read())
    assert 75.4571 == parsed_key_indicator_collection["USD"]
    assert 4529.59 == parsed_key_indicator_collection["Au"]
    assert 5667.14 == parsed_key_indicator_collection["Pd"]
    
def test_service_replied_to_cbr_daily(client):
    response = client.get("/cbr/daily")
    assert 200 == response.status_code

def test_clearing_all_assets(client):
    response_clearing = client.get("/api/asset/cleanup")
    assert 200 == response_clearing.status_code
    assert "there are no more assets" == response_clearing.data.decode(response_clearing.charset)
    assert 0 == len(ASSET_COLLECTION._asset_collection)

def test_can_not_add_asset_twice(client):
    response_clearing = client.get("/api/asset/cleanup")
    response_add_assets = client.get("/api/asset/add/EUR/stock/100/0.05")
    assert 200 == response_add_assets.status_code
    response_add_assets = client.get("/api/asset/add/EUR/stock/100/0.05")
    assert 403 == response_add_assets.status_code
    response_clearing = client.get("/api/asset/cleanup")

def test_service_can_add_show_assets(client):

    response_clearing = client.get("/api/asset/cleanup")

    response_add_asset = client.get("/api/asset/add/RUB/stock/1000/0.01")
    # from pdb import set_trace; set_trace()
    assert 200 == response_add_asset.status_code
    assert "Asset 'stock' was successfully added" == response_add_asset.data.decode(response_add_asset.charset)
    assert 1 == len(ASSET_COLLECTION._asset_collection)
    assert "stock" == ASSET_COLLECTION._asset_collection[0].name

    response_add_asset = client.get("/api/asset/add/EUR/deposit/100/0.05")
    assert 2 == len(ASSET_COLLECTION._asset_collection)
    assert "deposit" == ASSET_COLLECTION._asset_collection[1].name

    response_add_asset = client.get("/api/asset/add/EUR/house/10000/0.005")
    assert 3 == len(ASSET_COLLECTION._asset_collection)
    assert "house" == ASSET_COLLECTION._asset_collection[2].name


    response_show_assets = client.get("/api/asset/list")
    assert 200 == response_show_assets.status_code
    assert response_show_assets.is_json
    assert 3 == len(response_show_assets.json)
    assert all(4 == len(asset) for asset in response_show_assets.json) 
    assert "deposit" == response_show_assets.json[0][1]

    response_show_particular_assets = client.get("/api/asset/get?name=stock&name=house")
    # from pdb import set_trace; set_trace()
    assert 200 == response_show_particular_assets.status_code
    assert response_show_particular_assets.is_json
    assert 2 == len(response_show_particular_assets.json)
    assert all(4 == len(asset) for asset in response_show_particular_assets.json)
    assert "stock" == response_show_particular_assets.json[1][1]
    client.get("/api/asset/cleanup")

    # response_calculate_profit = client.get("/api/asset/calculate_revenue?period=3&period=5")
    #assert все замокано и переводится по корректным курсам в рубли

@patch('task_Yaropolov_Oleg_asset_web_service.download_cbr_daily')
@patch('task_Yaropolov_Oleg_asset_web_service.download_cbr_key_indicator')
def test_revenue_calculation_is_correct(mock_cbr_key_indicator, mock_cbr_daily, client):
    client.get("/api/asset/cleanup")

    mock_cbr_daily.return_value = open(CBR_CURRENCY_DAILY_LOCAL, encoding="utf8").read()
    mock_cbr_key_indicator.return_value = open(CBR_KEY_INDICATOR_LOCAL, encoding="utf8").read()

    capital = 10
    interest = 0.01
    periods = [1,3]

    client.get("/api/asset/cleanup")
    client.get(f"/api/asset/add/RUB/deposit1/{capital}/{interest}")
    client.get(f"/api/asset/add/EUR/deposit2/{capital}/{interest}")
    client.get(f"/api/asset/add/AMD/deposit3/{capital}/{interest}")
    client.get(f"/api/asset/add/Au/deposit4/{capital}/{interest}")

    daily_dict = return_cbr_daily()
    key_indicator_dict = return_cbr_key_indicators()

    exchange_rate = [
        1,
        key_indicator_dict["EUR"],
        daily_dict["AMD"],
        key_indicator_dict["Au"],
    ]

    profit_before_exchange = [capital * ((1.0 + interest) ** period - 1.0) for period in periods]
    profit = [sum([pbe * ex for ex in exchange_rate]) for pbe in profit_before_exchange]

    response_calculations = client.get(f"/api/asset/calculate_revenue?period={periods[0]}&period={periods[1]}")
    assert 200 == response_calculations.status_code
    assert response_calculations.is_json
    assert 2 == len(response_calculations.json)

    assert round(profit[0], 8) == response_calculations.json['1']
    assert round(profit[1], 8) == response_calculations.json['3']


