#%%
import requests
import pandas as pd
from datetime import date
import threading
import sqlalchemy


class NVEDataClient:
    base_url = "https://hydapi.nve.no/api/"
    version = "v1"
    observation_endpoint = base_url + version + "/Observations"
    parameters_endpoint = base_url + version + "/Parameters"
    stations_endpoint = base_url + version + "/Stations"
    series_endpoint = base_url + version + "/Series"

    def __init__(self, api_key):
        self.request_headers = {"Accept": "application/json", "X-API-Key": api_key}

    def get_parameters(self):
        param_res = requests.get(url=NVEDataClient.parameters_endpoint, headers=self.request_headers)
        param_res.raise_for_status()
        param_res_json = param_res.json()
        df_params = pd.DataFrame(param_res_json["data"])
        return df_params

    def get_stations(
        self,
        station_id="",
        station_name="",
        council_number="",
        council_name="",
        country_name="",
        active="1",
        polygon="",
    ):

        station_params = {
            "StationId": station_id,
            "StationName": station_name,
            "CouncilNumber": council_number,
            "CouncilName": council_name,
            "CountryName": country_name,
            "Active": active,
            "Polygon": polygon,  # WKT format
        }
        stations_res = requests.get(
            url=NVEDataClient.stations_endpoint, params=station_params, headers=self.request_headers
        )
        stations_res.raise_for_status()

        return pd.DataFrame(stations_res.json()["data"])

    def get_series(
        self,
        station_id="",
        station_name="",
        council_number="",
        council_name="",
        country_name="",
        datafrom="",
        polygon="",
    ):
        series_params = {
            "StationId": station_id,
            "StationName": station_name,
            "CouncilNumber": council_number,
            "CouncilName": council_name,
            "CountryName": country_name,
            "DataFrom": datafrom,
            "Polygon": polygon,  # WKT format
        }
        series_res = requests.get(url=NVEDataClient.series_endpoint, params=series_params, headers=self.request_headers)
        series_res.raise_for_status()

        return pd.DataFrame(series_res.json()["data"])

    def get_observations(self, station_id, parameter, resolution_time, from_date, to_date):
        obs_params = {
            "StationId": station_id,
            "Parameter": parameter,
            "ResolutionTime": resolution_time,  # "day"
            "ReferenceTime": f"{from_date.isoformat()}/{to_date.isoformat()}",
        }

        res = requests.get(url=NVEDataClient.observation_endpoint, params=obs_params, headers=self.request_headers)
        res.raise_for_status()

        res_json = res.json()
        if res_json["itemCount"] != 1:
            raise NotImplementedError("No handling of multiple series. Query one series at the time.")

        observations = res_json["data"][0].pop("observations")
        df = pd.DataFrame(observations)
        df["time"] = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True)

        df_meta = pd.DataFrame(res_json["data"][0], index=[0])

        return df, df_meta


class DbClient:
    def __init__(self, connection_string, db_name):
        self.connection = connection_string
        self.engine = sqlalchemy.create_engine(connection_string)
        self.connection = self.engine.connect()
        self.db_name = db_name
        self.lock = threading.Lock()

    def get_price_data(self, from_date, to_date):
        if isinstance(from_date, date):
            from_date = str(from_date)
        if isinstance(to_date, date):
            to_date = str(to_date)
        query = """
            SELECT
                Tidspunkt,
                Verdi
            FROM
                {0}.dbo.nordpool
            WHERE
                Tidspunkt >= CAST('{1}' as date)
                AND Tidspunkt < CAST('{2}' as date)
            ORDER BY
                Tidspunkt
        """.format(
            self.db_name, from_date, to_date
        )
        df = pd.read_sql_query(query, self.connection)

        return df
