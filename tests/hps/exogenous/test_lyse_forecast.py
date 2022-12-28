import pytest
import numpy as np
import pytz
import datetime
from pathlib import Path

from hps.exogenous.lyse_forecast import ReadInflow, ReadPrice, PriceMetaData


@pytest.fixture()
def meta_data():
    local_tz = pytz.timezone("Europe/Oslo")
    forecast_week = 10
    forecast_year = 2020
    forecast_at_time = datetime.datetime.strptime("{weekday}-{week}-{year}".format(
            weekday=1, week=forecast_week, year=forecast_year), "%u-%V-%G")
    forecast_at_time = local_tz.localize(forecast_at_time) # Add timezone

    pri_file_base = "/media/data/hydro_scheduling/sftp/marked/pris/ProdRisk-Prisrekker/"
    pri_file = pri_file_base + f"{forecast_year}/uke-{forecast_week}/uke-{forecast_week}.pri"
    pri_file = Path(pri_file)

    return PriceMetaData(pri_file, local_tz)

@pytest.fixture()
def read_price(meta_data):
    return ReadPrice(meta_data)

@pytest.fixture() 
def read_inflow(meta_data):
    INFLOW_FILE = "/media/data/hydro_scheduling/sftp/inflow/historical/inflow_data.csv"    
    hist_years = np.arange(1985,2015)
    return ReadInflow(INFLOW_FILE, hist_years, local_tz=meta_data.local_tz)


@pytest.mark.skip(reason="Slow test")
def test_shape(read_price, read_inflow, meta_data):
    price = read_price.get_df().values
    inflow = read_inflow.get_dict(meta_data)["Flørli"].values

    assert price.shape == inflow.shape