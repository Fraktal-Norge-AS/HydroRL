from hps_api_client.poco import *
from hps_api_client.apiclient import ApiClient
import tqdm

class ApiProxy:
    """Wrapper around the HydroRL API.
    
    Part of the HydroRL SDK, facilitates access to the HydroRL API by constructing
    client-side objects and pandas dataframes from the API results.
    """
    
    def __init__(self, uri : str = "http://hps/api/v1/"):
        """Constructs the proxy and binds it the the provided uri.
        
        Parameters
        ----------
        uri : Uri for the API instance.
        user_name : Assigned username
        password : Assigned password"""

        self.uri = uri
        self.api_client = ApiClient(uri, True)

    def get_hydro_systems(self) -> ApiHydroSystemCollection:
        """Get list of all hydrosystems configured on the server."""

        hydro_systems = self.api_client.get_hydro_systems()
        return ApiHydroSystemCollection(hydro_systems)

    def get_projects(self) -> ApiProjectCollection:
        """Get all projects created by any user.
        
        Projects are a means by which users can organise runs that are related, 
        e.g. this weeks runs for a given hydrosystem.
        """

        projects = self.api_client.get_projects()
        return ApiProjectCollection(projects)

    def create_project(self, name : str, hydro_system : ApiHydroSystem) -> ApiProject:
        """Creates and returns a new project with the specified name.
        
        The new project will be tied to the specified hydro system.
        
        Parameters
        ----------
        name : The name of the project.
        hydro_system : The hydro system the project will operate on
        """

        new_project = self.api_client.create_project(name, hydro_system.uid)
        return ApiProject(new_project)

    def get_forecasts(self, hydro_system : ApiHydroSystem) -> ApiForecastCollection:
        """Get a collection of all forecasts configured for the specified hydro system.
        
        Parameters
        ----------
        hydro_system : The hydro system to retrieve forecasts for.
        """

        forecasts = self.api_client.get_forecasts(hydro_system.uid)
        return ApiForecastCollection(forecasts)

    def get_forecast_scenarios(self, forecast : ApiForecast) -> ApiForecastScenarios:
        """Get a list of scenarios available for the specified forecast

        Parameters
        ----------
        forecast : The forecast to retrieve scenarios for.
        """

        scen = self.api_client.get_forecast_scenarios(forecast.uid)
        return ApiForecastScenarios(scen).scenarios

    def get_scenario_data(self, forecast : ApiForecast, scenario : str) -> pd.DataFrame:
        """Get data for a single scenario.

        Parameters
        ----------
        forecast : The forecast to retrieve data for.
        scenario : The scenario to retrieve data for.
        """

        data = ApiForecastScenario(self.api_client.get_forecast_data(forecast.uid, scenario))

        df = pd.DataFrame.from_dict({"Inflow" : data.inflowSeries, "Price" : data.priceSeries})
        df['Date']= pd.to_datetime(data.timeIndex)
        df.set_index("Date", inplace=True)

        return df

    def get_forecast_data(self, forecast : ApiForecast) -> pd.DataFrame:
        """Get data for the entire forcast.

        The resulting Dataframe is MultiIndex'ed with price and inflow for each scenario.
        Since retrieval is somewhat time consuming, a progressbar is displayed while loading the dataframe.

        Parameters
        ----------
        forecast : The forecast to retrieve data for.
        """

        scenarios = self.get_forecast_scenarios(forecast)
        data = {}

        for scenario in tqdm.tqdm(scenarios):
            scen_data = ApiForecastScenario(self.api_client.get_forecast_data(forecast.uid, scenario))
            data[("Price", scenario)] = scen_data.priceSeries
            data[("Inflow", scenario)] = scen_data.inflowSeries


        df = pd.DataFrame(data)
        df["Date"] = pd.to_datetime(scen_data.timeIndex)
        df.set_index("Date", inplace=True)
        return df

    def add_forecast(self, forecast_name : str, hydro_system : ApiHydroSystem, data : pd.DataFrame):
        """Add a new forecast associated with the specified hydro system.

        The input Dataframe must be MultiIndex'ed with price and inflow for each scenario.
        Columns format:
        Date : pandas DateTimeIndex
        ("Price", scen1)  : float
        ("Inflow", scen1) : float
        ("Price", scen2)  : float
        ("Inflow", scen2) : float
        ...
        etc

        Since uploading forecasts is time consuming, a progressbar is displayed during the operation.

        Parameters
        ----------
        forecast_name : The identifier for the new forecast.
        hydro_system : The hydro system this forecast applies to.
        data : A dataframe containing inflow and price for each scenario.
        """

        is_multi_index = isinstance(data.columns, pd.MultiIndex)
        valid_colums = False

        if is_multi_index:
            p_and_f = list(set([i[0] for i in data.columns]))
            valid_colums = len(p_and_f) == 2 and "Price" in p_and_f and "Inflow" in p_and_f

        if not valid_colums:
            raise ValueError("Argument 3 : Dataframe index must be a MultiIndex of the format [('Price,'Scenario'), ('Inflow',Scenario') .. ]")

        if data.isnull().sum().sum() > 0:
            raise ValueError("Argument 3 : No empty cells (NaN) allowed in DataFrame")

        forecast = ApiForecast(self.api_client.create_forecast(forecast_name, hydro_system.uid))

        scenarios = list(set([i[1] for i in data.columns]))

        for scenario in tqdm.tqdm(scenarios):
            fc = ApiForecastScenario({})
            fc.timeIndex = [str(t) for t in data.index]
            fc.inflowSeries = [float(t) for t in data[("Inflow", scenario)]]
            fc.priceSeries = [float(p) for p in data[("Price", scenario)]]
            self.api_client.add_forecast_scenario(forecast.uid, scenario, fc.to_dict())

        print("Forecast '{}' with {} scenarios succeessfully uploaded to server".format(forecast_name, len(scenarios)))

    def run(self, project : ApiProject, forecast : ApiForecast, settings : RunSettings) -> ApiRun:
        """Start a run for the specified project using the specified forecast and settings.
        
        This method starts an asynchronous job that may run for hours. Status for the job can be 
        retrieved using the get_runs and show_progress mothods. The job can be terminated by invoking
        the terminate_run method.
        
        Parameters
        ----------
        project : The project context for the run.
        forecast : The forecast used during training.
        settings : Configuration for the run.        
        """

        new_run = self.api_client.run(project.uid, forecast.uid, settings.to_dict())
        return ApiRun(new_run)

    def evaluate(self, run : ApiRun, forecast : ApiForecast, settings : RunSettings) -> ApiRun:
        """Starts an evalaution using the specified forecast and settings.
        
        The evalaution will be executed on the best performing agent for the specified run.
        This job is performed asynchronously, and the result, when available, can be
        retrieved through the get_evaluation method. By calling get_evalautions on the
        current project, you can get an indication of when the evaluation is complete.
        
        Parameters
        ----------
        run : The pretrained run that will be used for the evaluation.
        forecast : The forecast that will be evaluated.
        settings : Configuration for the evaluation.
        """

        new_run = self.api_client.evaluate(run.uid, forecast.uid, settings.to_dict())
        return ApiRun(new_run)

    def get_reservoirs(self, hydro_system : ApiHydroSystem) -> ApiReservoirCollection:
        """Get a collection of reservoirs for the specified hydro system."""

        res = self.api_client.get_reservoirs(hydro_system.uid)
        return ApiReservoirCollection(res)

    def get_settings_template(self, project : ApiProject) -> RunSettings:
        """Get a settings object tailored to the specified project.
        
        The settings object can be used to start a run or to execute an evaluation.

        Parameters
        ----------
        project : The project to customize the settings object for.
        """

        template = self.api_client.get_settings_template(project.uid)
        return RunSettings(template)

    def get_runs(self, project : ApiProject) -> ApiRunCollection:
        """Get all runs for the specified project.
        
        Includes currently executing runs.

        Parameters
        ----------
        project : The project to retrieve runs for.
        """

        runs = self.api_client.get_runs(project.uid)
        return ApiRunCollection(runs)

    def get_evaluations(self, project : ApiProject) -> ApiRunCollection:
        """Get all evaluations performed for the specified project.
        
        Includes currently executing evalautions.

        Parameters
        ----------
        project : The project to retrieve evalautions for.
        """

        runs = self.api_client.get_evaluations(project.uid)
        return ApiRunCollection(runs)
    
    def show_progress(self, run : ApiRun, **plt_kwargs):
        """Presents progress information for the specified run.
        
        Parameters
        ----------
        run : The run to show progress for.
        """

        self.api_client.show_progress(run.uid, **plt_kwargs)

        self.api_client.show_progress(run.uid, **plt_kwargs)
    def plot_solution(self, run : ApiRun):
        """Presents the best solution achived by any agent in the run.
        
        Parameters
        ----------
        run : The run to be presented.
        """
       
        self.api_client.plot_solution(run.uid)

    def get_solution(self, run : ApiRun) -> pd.DataFrame:
        """Get the best solution achived by any agent in the run.
        
        The result is returned as a multiindex pandas DataFrame. The first index is 
        the result parameter and the second index is the forecast scenario.

        Parameters
        ----------
        run : The run to get the solution for.
        """

        solution = self.api_client.best_solution(run.uid)
        solution = ApiReportData(solution)
        return self.__build_data_frame(solution)

    def get_evaluation(self, evaluation : ApiRun) -> pd.DataFrame:
        """Get the results of an evaluation.
        
        The result is returned as a multiindex pandas DataFrame. The first index is 
        the result parameter and the second index is the forecast scenario.

        Parameters
        ----------
        evaluation : The evalaution to get the results for.
        """

        solution = self.api_client.evaluation_results(evaluation.uid)
        solution = ApiReportData(solution)
        return self.__build_data_frame(solution)
        
    def plot_evaluation(self, evaluation : ApiRun):
        """Presents the results of an evaluation.
        
        Parameters
        ----------
        evaluation : The evalaution to be presented.
        """

        self.api_client.plot_evaluation(evaluation.uid)

    def terminate_run(self, run : ApiRun):
        """Terminates the specified run.
        
        It may take a while to finalize a run, and actual termination is 
        achived when the run has an end time.

        Parameters
        ----------
        run : The run to terminate.
        """
        self.api_client.terminate_run(run.uid)

    def build_data_frame(self, solution : ApiReportData) -> pd.DataFrame:
        return self.__build_data_frame(solution)

    def __build_data_frame(self, solution : ApiReportData) -> pd.DataFrame:
        data = {}
        for episode in solution.episodes:
            for series in episode.series:
                data[(series.name, episode.name)] = series.values
        
        df = pd.DataFrame(data)
        df['Date']= pd.to_datetime(solution.timeStamps)
        df.set_index("Date", inplace=True)

        return df


