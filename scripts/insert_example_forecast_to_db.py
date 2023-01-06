import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import pandas as pd

from hps_api_client.apiproxy import ApiProxy


API_URI = "http://localhost:5400/api/v1/"

df = pd.read_csv("data/example_forecast.csv", header=[0,1], index_col=0, parse_dates=True)
    
client = ApiProxy(uri=API_URI)

hydro_systems = client.get_hydro_systems()

for hs in hydro_systems:
    client.add_forecast(
        forecast_name="My example forecast",
        hydro_system=hs,
        data=df)

