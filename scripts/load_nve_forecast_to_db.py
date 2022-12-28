#%%

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from pathlib import Path

import configparser
import datetime

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.appsettings import appSettings
import urllib3 as url3
import json

from hps.exogenous.nve_forecast import DbClient, NVEDataClient
from hps.exogenous.lyse_forecast import populate_forecast_from_df_to_db
from hps.exogenous.inflow_and_price import get_start_end_time_forecast, read_forecast_from_db

#%%
config = configparser.ConfigParser(interpolation=None)
config.read(Path.cwd()/'scripts/configurations.ini')

api_key = config['NVE API']['API Key']
db_charset = config['Spot Price DB']["Charset"]
db_ip = config['Spot Price DB']["IP"]
db_name = config['Spot Price DB']['Name']
db_user = config['Spot Price DB']['User']
db_pw = config['Spot Price DB']['PW']

#%%
hpsdb_connection_string = appSettings.get_connection_string()

nve_client = NVEDataClient(api_key)

from_date = datetime.date(2013,1,1)
to_date = datetime.date(2020,12,31)

def get_inflow(from_date, to_date):
    df_i, df_i_meta = nve_client.get_observations(station_id="62.5.0", parameter="1001", resolution_time="60",
        from_date=from_date, to_date=to_date)

    df_i = df_i[["value"]]

    # Scale inflow to having expected yearly inflow of 100 Mm3 
    mean_yearly_inflow = df_i.groupby(df_i.index.year).mean().mean()*8760*3600/10**6
    df_i = 100 * df_i / mean_yearly_inflow

    # Append year 2013 to end
    df_t = df_i.loc[df_i.index.year.isin([2013])]
    df_t.index = df_t.index.map(lambda t: t.replace(year=df_i.index[-1].year + 1))
    df_i = pd.concat([df_i, df_t])
    return df_i

def get_price(from_date, to_date):
    db_connection_string = f'mssql+pymssql://{db_user}:{db_pw}@{db_ip}/?charset={db_charset}'
    db_client = DbClient(db_connection_string, db_name)

    df_p = db_client.get_price_data(from_date, to_date)
    df_p.set_index("Tidspunkt", inplace=True)

    # Append year 2013 to end
    df_t = df_p.loc[df_p.index.year.isin([2013])]
    df_t.index = df_t.index.map(lambda t: t.replace(year=df_p.index[-1].year + 1))
    df_p = pd.concat([df_p, df_t])
    return df_p


df_i = get_inflow(from_date, to_date)
df_p = get_price(from_date, to_date)
#%%

# Create inflow and price forecast prognosis
prognosis_start_time = pd.Timestamp("2021-01-01T00:00Z")

dd_p = pd.DataFrame()
dd_i = pd.DataFrame()
for year in df_p.index.year.unique()[:-1]:
    df_pt = df_p.loc[df_p.index.year.isin([year, year + 1])]
    df_pt.index = prognosis_start_time + (df_pt.index - df_pt.index[0])
    df_pt.rename(columns={"Verdi": year}, inplace=True)
    dd_p = pd.concat([dd_p, df_pt], axis=1)

    df_it = df_i.loc[df_i.index.year.isin([year, year + 1])]
    df_it.index = prognosis_start_time + (df_it.index - df_it.index[0])
    df_it.rename(columns={"value": year}, inplace=True)
    dd_i = pd.concat([dd_i, df_it], axis=1)

dd_p = dd_p.ffill()
dd_p = dd_p/10 # NOK/MWh -> EUR/MWh
dd_i = dd_i.ffill()

if not (dd_i.index == dd_p.index).all(): # Assert equal time index
    raise Exception("Index of inflow and price not the same.")

# dd_p.iloc[:760,-2].plot()

# session = RlBuilder.create_session()
# forecast_id = 27
# system = "small"
# forecast_start, forecast_end = get_start_end_time_forecast(session, forecast_id)

# price_inflow_data = read_forecast_from_db(session, 
#     forecast_id, hydro_system=system,
#     from_date=forecast_start, to_date=forecast_start+pd.Timedelta(days=30))

# price_inflow_data.price.iloc[:300,:].plot()
# price_inflow_data.inflow.iloc[:300,:].plot()


#%%
#Set up metadata for webreq
webreq=url3.PoolManager(num_pools=1)
base_uri = "http://leviathan:5400/api/v1/"
# Get hydrosystems
response = webreq.request("GET", base_uri + "hydrosystems")
hs_dt = pd.read_json(response.data)
#%%
# Create forecasts
forecast_uid = []
for index, row in hs_dt.iterrows():
    hs_uid = row["uid"]
    forecast_name = "NVE+Spot forecast"
    response = webreq.request("POST", base_uri + "forecasts?hydrosystemUid={0}&forecastName={1}".format(hs_uid, forecast_name))
    forecast_uid.append(json.loads(response.data)["uid"])
#%%
years = list(dd_p.columns)
print("loading a total of {0} forecasts".format(len(forecast_uid)))
for forecast in forecast_uid:
    print("Loading forecast_uid {0}".format(forecast))
    for year in years:
        print("\tLoading scenario {0}".format(year))
        ht = {}
        ht["inflowSeries"] = dd_i[year].to_list()
        ht["priceSeries"] = dd_p[year].to_list()
        ht["timeIndex"] = dd_p.index.strftime("%Y-%m-%dT%H:%M:%S.%fZ").to_list()
        forecast_body = json.dumps(ht)

        response = webreq.request(
            method="POST", 
            url=base_uri + "forecasts/{0}?scenario={1}".format(forecast, year), 
            body=forecast_body,
            headers={"Content-Type": "application/json"})
        if(response.data != b''):
            print(response.data)



def smoothed_initial_price_forecast():
#%%
    import matplotlib.pyplot as plt
    import numpy as np

    initial_price = dd_p.iloc[0,:].mean()

    n = len(dd_p)
    nn = 2000
    tau = np.array([np.exp(-i*10/nn) for i in np.arange(n)])
    plt.plot(tau[:nn])

    df = pd.DataFrame()
    for col in dd_p:
        df[col] = dd_p[col]*(1-tau) + initial_price*tau

    df[:nn].plot()

    # # Write inflow and price to HPSDB
    engine = create_engine(hpsdb_connection_string)
    Session = sessionmaker(bind=engine)
    session = Session()

    hydro_systems = ["small", "medium", "large"]
    for hs in hydro_systems:
        populate_forecast_from_df_to_db(session, dd_i, df, dd_i.index, hs, forecast_name="NVE+Spot+Smoothing")


def deterministic_price():
    df = pd.DataFrame()
    for col in dd_p:
        df[col] = dd_p[col]*(1-tau) + initial_price*tau

    df[:nn].plot()

#%%
    # # Write inflow and price to HPSDB
    engine = create_engine(hpsdb_connection_string)
    Session = sessionmaker(bind=engine)
    session = Session()
    for col in dd_p.columns:
        df = pd.DataFrame()
        for c in dd_p.columns:
            df[c] = dd_p[col]

        hydro_systems = ["small", "medium", "large"]
        for hs in hydro_systems:
            populate_forecast_from_df_to_db(session, dd_i, df, dd_i.index, hs, forecast_name=f"NVE+{col}+DetPrice")

#%%

def deterministic_price_and_inflow():

#%%
    year = 2015
    df_p = dd_p[[year]].copy()
    df_i = dd_i[[year]].copy()

#%% # Write inflow and price to HPSDB
    engine = create_engine(hpsdb_connection_string)
    Session = sessionmaker(bind=engine)
    session = Session()

#%%
    hydro_systems = ["small", "medium", "large"]
    for hs in hydro_systems:
        populate_forecast_from_df_to_db(session, df_i, df_p, df_i.index, hs, forecast_name=f"NVE+{year}+DetPriceInflow") 

#%%
def misc():
    # %%

    from hps.exogenous.inflow_and_price import InflowPriceForecastData, InflowPriceSampler, get_start_end_time_forecast, read_forecast_from_db
    import matplotlib.pyplot as plt

    ip_data = InflowPriceForecastData("small", dd_i, dd_p)
    time_index = pd.date_range(start=dd_p.index[0], periods=104, freq='1W')
    ip_sampler = InflowPriceSampler(ip_data, time_index, n_clusters=5, is_eval=False)
    ip_sampler.df_i.plot()
    ip_sampler.df_p.plot()
    
    # %%
    fig, axs = plt.subplots(nrows=2, ncols=1)
    for i in range(10):
        vals, _ = ip_sampler.sample_episode()
        axs[0].plot(vals[:,0])
        axs[1].plot(vals[:,1])    

    # %%
    forecast_start, _ = get_start_end_time_forecast(session, 408)

    train_time_index = pd.date_range(
        start=forecast_start,
        periods=94 + 1,
        freq="1W")

    price_inflow_data = read_forecast_from_db(session, 
        408, hydro_system="large",
        from_date=forecast_start, to_date=train_time_index[-1])

    price_inflow_data.inflow.plot()
    price_inflow_data.price.plot()
    # %%

    train_inflow_price_sampler = InflowPriceSampler(
        price_inflow_data, train_time_index, seed=42, n_clusters=3)

    train_inflow_price_sampler.df_i.plot()
    train_inflow_price_sampler.df_p.plot()
    # %%
    rule = '1W'
    # rule = '4D'
    # base_date = pd.to_datetime(train_time_index[0]) - pd.tseries.frequencies.to_offset(rule)
    # s.loc[base_date] = np.nan

    df_i = price_inflow_data.inflow[
        (price_inflow_data.inflow.index >= train_time_index[0]) & (price_inflow_data.inflow.index <= train_time_index[-1])
    ].resample(rule=rule, origin='start').mean()

    df_i.plot()
    #%%
    df_i = df_i[df_i.index.isin(train_time_index)]
    df_i.plot()
