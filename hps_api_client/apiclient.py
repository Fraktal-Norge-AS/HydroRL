import pandas as pd
import requests
from matplotlib import pyplot as plt
from urllib import parse

def get_attr(df, lookup, value, value_col):
    return df.loc[df[lookup] == value, value_col].iloc[0]

class ApiClient:
    def __init__(self, uri, return_json = False):
        self.uri = uri
        self.return_json = return_json
    
    def prep_content(self, response):
        json_data = response.json()
        dataframe = pd.json_normalize(json_data)
        return json_data, dataframe    

    def error_check(self, response):
        if response.status_code != requests.codes.ok:
            print(response.content)
            response.raise_for_status()

    def fetch(self, uri):
        response = requests.get(uri)
        self.error_check(response)
        return self.prep_content(response)

    def post_no_body(self, uri):
        response = requests.post(uri)
        self.error_check(response)
        return self.prep_content(response)

    def post_with_body(self, uri, body):
        response = requests.post(uri, json = body)
        self.error_check(response)
        return self.prep_content(response)

    def post_with_body_no_response(self, uri, body):
        response = requests.post(uri, json = body)
        self.error_check(response)

    def put_with_body(self, uri, body):
        response = requests.put(uri, json = body)
        self.error_check(response)
        return self.prep_content(response)
    
    def action(self, uri):
        response = requests.put(uri)
        self.error_check(response)
        return response
    
    def get_hydro_systems(self):
        hydro_systems_uri = self.uri + "hydrosystems"

        hydro_systems, df = self.fetch(hydro_systems_uri)
        return hydro_systems if self.return_json else df 
    
    def get_projects(self):
        projects, df = self.fetch(self.uri + "projects")
        return projects if self.return_json else df 
    
    def create_project(self, name, hydro_system_uid):
        args = {"name" : name, "hydrosystemUid" : hydro_system_uid}
        create_project_uri = self.uri + "projects?" + parse.urlencode(args)

        new_project, df = self.post_no_body(create_project_uri)
        return new_project if self.return_json else df 
    
    def get_forecasts(self, hydro_system_uid):
        forecast_uri = self.uri + "hydrosystems/{}/forecasts".format(hydro_system_uid)

        forecasts, df = self.fetch(forecast_uri)
        return forecasts if self.return_json else df 

    def get_forecast_scenarios(self, forecast_uid):
        forecast_uri = self.uri + "forecasts/{}/".format(forecast_uid)

        forecast_scenarios, df = self.fetch(forecast_uri)
        return forecast_scenarios if self.return_json else df

    def get_forecast_data(self, forecast_uid, forecast_scenario):        
        forecast_uri = self.uri + "forecasts/{}/scenarios/{}".format(forecast_uid, forecast_scenario)
    
        forecast_data, df = self.fetch(forecast_uri)
        return forecast_data if self.return_json else df

    def create_forecast(self, forecast_name, hydro_system_uid):
        args = {"hydrosystemUid" : hydro_system_uid, "forecastName" : forecast_name}
        forecast_uri = self.uri + "forecasts?" + parse.urlencode(args)
    
        new_forecast, df = self.post_no_body(forecast_uri)
        return new_forecast if self.return_json else df

    def add_forecast_scenario(self, forecast_uid, scanario_name, data):
        args = {"scenario" : scanario_name}
        post_uri = self.uri + "forecasts/{}?{}".format(forecast_uid, parse.urlencode(args))        
        self.post_with_body_no_response(post_uri, data)

    def run(self, project_uid, forecast_uid, settings):
        run_uri = self.uri + "projects/" + project_uid + "/run?forecastUid=" + forecast_uid

        new_run, df = self.put_with_body(run_uri, settings)
        return new_run if self.return_json else df

    def evaluate(self, run_uid, forecast_uid, settings):
        run_uri = self.uri + "projectruns/" + run_uid + "/evaluate?forecastUid=" + forecast_uid
        new_run, df = self.put_with_body(run_uri, settings)
        return new_run if self.return_json else df 
    
    def get_reservoirs(self, hydro_system_uid):
        uri = self.uri + "hydrosystems/{}/reservoirs".format(hydro_system_uid)
        res, df = self.fetch(uri)
        return res if self.return_json else df 
    
    def get_settings_template(self, project_uid):
        uri = self.uri + "projects/{}/runsettingstemplate".format(project_uid)
        res, df = self.fetch(uri)
        return res
    
    def get_runs(self, uid):
        run_uri = self.uri + "projects/" + uid + "/projectruns"
        run, df = self.fetch(run_uri)
        return run if self.return_json else df 

    def get_evaluations(self, uid):
        run_uri = self.uri + "projects/" + uid + "/evaluations"
        run, df = self.fetch(run_uri)
        return run if self.return_json else df 

    def get_run_details(self, uid, tag = "Best return", plot_only=True):
        details_uri = self.uri + "projectruns/" + uid + "/rundetails"
        details, _ = self.fetch(details_uri)

        test_return_datas = [d for d in details["status"] if d["name"] == tag]

        off = 0
        for test_return_data in test_return_datas:
            plt.plot(test_return_data["steps"][off:], test_return_data["values"][off:])

        if not plot_only:
            return test_return_datas

            
    def show_progress(self, uid, **plt_kwargs):
        details_uri = self.uri + "projectruns/" + uid + "/progress"

        details, _ = self.fetch(details_uri)
        test_return_datas = details["status"]# [d for d in details["status"] if d["name"] == "Best return"]

        off = 0
        for test_return_data in test_return_datas:
            plt.plot(test_return_data["steps"][off:], test_return_data["values"][off:], **plt_kwargs)  
            
            
    def terminate_run(self, uid):
        terminate_uri = self.uri + "projectruns/" + uid + "/terminate"
        rep = self.action(terminate_uri)
        
        
    def best_solution(self, uid):
        data_uri = self.uri + "projectruns/" + uid + "/solution"
        data, df = self.fetch(data_uri)
        return data

    def evaluation_results(self, uid):
        data_uri = self.uri + "evaluations/" + uid
        data, df = self.fetch(data_uri)
        return data
    
    def filter_series(self, series):
        return [s["name"] for s in series if not ("Agent" in s["name"] or "vol_" in s["name"] or "eward" in s["name"])]
    
    def plot_data(self, data):
        all_episodes = data["episodes"]
        num_episodes = len(all_episodes)

        if num_episodes < 1:
            return "Data si not yet available"

        series_names = self.filter_series(all_episodes[0]["series"])
        
        num_series = len(series_names)
        
        num_cols = 2
        num_rows = int(num_series/num_cols + 0.5)
        fig, ax = plt.subplots(num_rows, num_cols, figsize=(20,50))
        
        ax_lookup = {}
        
        for i, series_name in enumerate(sorted(series_names)):
            row, col = i // 2, i % 2
            ax_lookup[series_name] = ax[row,col]
        
        for data in all_episodes:
            all_series = data["series"]
            all_series = [s for s in all_series if not ("Agent" in s["name"] or "vol_" in s["name"] or "eward" in s["name"]) ]


            for i, series in enumerate(all_series):
                name = series["name"]
                vals = series["values"]
                ax = ax_lookup[name]

                ax.plot(vals, label=data["name"])
                ax.set_title(name)        
    
    def plot_solution(self, uid):
        data = self.best_solution(uid)
        self.plot_data(data)
        
    def plot_evaluation(self, uid):
        data = self.evaluation_results(uid)
        self.plot_data(data)
