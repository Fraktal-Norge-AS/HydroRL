import pandas as pd
import json
from enum import Enum

class ApiProject:
    def __init__(self, json):
        self.hydroSystem = ApiHydroSystem(json["hydroSystem"])
        self.name = json["name"]
        self.uid = json["uid"]

    def to_dict(self):
        json = {}
        json["hydroSystem"] = self.hydroSystem.to_dict() if self.hydroSystem is not None else None
        json["name"] = self.name
        json["uid"] = self.uid
        return json

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiProjectCollection:
    def __init__(self, json):
        self.values = [ApiProject(p) for p in json]

    def to_dict(self):
        return [p.to_dict() for p in self.values]

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiHydroSystem:
    def __init__(self, json):
        self.description = json["description"]
        self.name = json["name"]
        self.uid = json["uid"]

    def to_dict(self):
        json = {}
        json["description"] = self.description
        json["name"] = self.name
        json["uid"] = self.uid
        return json

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiHydroSystemCollection:
    def __init__(self, json):
        self.values = [ApiHydroSystem(p) for p in json]

    def to_dict(self):
        return [p.to_dict() for p in self.values]

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiReservoir:
    def __init__(self, json):
        self.minVolume = json["minVolume"]
        self.maxVolume = json["maxVolume"]
        self.name = json["name"]
        self.uid = json["uid"]

    def to_dict(self):
        json = {}
        json["minVolume"] = self.minVolume
        json["maxVolume"] = self.maxVolume
        json["name"] = self.name
        json["uid"] = self.uid
        return json

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiReservoirCollection:
    def __init__(self, json):
        self.values = [ApiReservoir(p) for p in json]

    def to_dict(self):
        return [p.to_dict() for p in self.values]

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiForecast:
    def __init__(self, json):
        self.name = json["name"]
        self.uid = json["uid"]

    def to_dict(self):
        json = {}
        json["name"] = self.name
        json["uid"] = self.uid
        return json

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiForecastCollection:
    def __init__(self, json):
        self.values = [ApiForecast(p) for p in json]

    def to_dict(self):
        return [p.to_dict() for p in self.values]

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiForecastScenarios:
    def __init__(self, json):
        self.scenarios = None if not "scenarios" in json else json["scenarios"]

    def to_dict(self):
        json = {}
        json["scenarios"] = self.scenarios
        return json

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiForecastScenariosCollection:
    def __init__(self, json):
        self.values = [ApiForecastScenarios(p) for p in json]

    def to_dict(self):
        return [p.to_dict() for p in self.values]

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiForecastScenario:
    def __init__(self, json):
        self.timeIndex = None if not "timeIndex" in json else json["timeIndex"]
        self.inflowSeries = None if not "inflowSeries" in json else json["inflowSeries"]
        self.priceSeries = None if not "priceSeries" in json else json["priceSeries"]

    def to_dict(self):
        json = {}
        json["timeIndex"] = self.timeIndex
        json["inflowSeries"] = self.inflowSeries
        json["priceSeries"] = self.priceSeries
        return json

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiForecastScenarioCollection:
    def __init__(self, json):
        self.values = [ApiForecastScenario(p) for p in json]

    def to_dict(self):
        return [p.to_dict() for p in self.values]

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiRun:
    def __init__(self, json):
        self.startTime = None if not "startTime" in json else json["startTime"]
        self.endTime = None if not "endTime" in json else json["endTime"]
        self.settings = RunSettings(json["settings"])
        self.forecast = ApiForecast(json["forecast"])
        self.name = json["name"]
        self.uid = json["uid"]

    def to_dict(self):
        json = {}
        json["startTime"] = self.startTime
        json["endTime"] = self.endTime
        json["settings"] = self.settings.to_dict() if self.settings is not None else None
        json["forecast"] = self.forecast.to_dict() if self.forecast is not None else None
        json["name"] = self.name
        json["uid"] = self.uid
        return json

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiRunCollection:
    def __init__(self, json):
        self.values = [ApiRun(p) for p in json]

    def to_dict(self):
        return [p.to_dict() for p in self.values]

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class EndStateIncentive(Enum):
    MeanEnergyPrice = "MeanEnergyPrice"
    LastEnergyPrice = "LastEnergyPrice"
    ProvidedEndEnergyPrice = "ProvidedEndEnergyPrice"
    Off = "Off"

class Noise(Enum):
    StandardDev = "StandardDev"
    White = "White"
    Off = "Off"

class StepResolution(Enum):
    Day = "Day"
    Week = "Week"
    Hour = "Hour"

class AgentAlgorithm(Enum):
    SAC = "SAC"
    A2C = "A2C"
    DDPG = "DDPG"
    TD3 = "TD3"
    PPO = "PPO"

class RunSettings:
    def __init__(self, json):
        self.comment = json["comment"]
        self.trainEpisodes = json["trainEpisodes"]
        self.endStateIncentive = EndStateIncentive[json["endStateIncentive"]]
        self.noise = Noise[json["noise"]]
        self.previousProjectRunUid = json["previousProjectRunUid"]
        self.previousQValueProjectRunUid = json["previousQValueProjectRunUid"]
        self.discountRate = json["discountRate"]
        self.startVolumes = None if not "startVolumes" in json else json["startVolumes"]
        self.stepsInEpisode = json["stepsInEpisode"]
        self.stepResolution = StepResolution[json["stepResolution"]]
        self.stepFrequency = json["stepFrequency"]
        self.randomizeStartVolume = json["randomizeStartVolume"]
        self.rewardScaleFactor = json["rewardScaleFactor"]
        self.forecastClusters = json["forecastClusters"]
        self.priceOfSpillage = json["priceOfSpillage"]
        self.endEnergyPrice = json["endEnergyPrice"]
        self.evaluationEpisodes = json["evaluationEpisodes"]
        self.evaluationInterval = json["evaluationInterval"]
        self.agentAlgorithm = AgentAlgorithm[json["agentAlgorithm"]]

    def to_dict(self):
        json = {}
        json["comment"] = self.comment
        json["trainEpisodes"] = self.trainEpisodes
        json["endStateIncentive"] = self.endStateIncentive.value
        json["noise"] = self.noise.value
        json["previousProjectRunUid"] = self.previousProjectRunUid
        json["previousQValueProjectRunUid"] = self.previousQValueProjectRunUid
        json["discountRate"] = self.discountRate
        json["startVolumes"] = self.startVolumes
        json["stepsInEpisode"] = self.stepsInEpisode
        json["stepResolution"] = self.stepResolution.value
        json["stepFrequency"] = self.stepFrequency
        json["randomizeStartVolume"] = self.randomizeStartVolume
        json["rewardScaleFactor"] = self.rewardScaleFactor
        json["forecastClusters"] = self.forecastClusters
        json["priceOfSpillage"] = self.priceOfSpillage
        json["endEnergyPrice"] = self.endEnergyPrice
        json["evaluationEpisodes"] = self.evaluationEpisodes
        json["evaluationInterval"] = self.evaluationInterval
        json["agentAlgorithm"] = self.agentAlgorithm.value
        return json

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class RunSettingsCollection:
    def __init__(self, json):
        self.values = [RunSettings(p) for p in json]

    def to_dict(self):
        return [p.to_dict() for p in self.values]

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiTimeSeries:
    def __init__(self, json):
        self.name = json["name"]
        self.values = None if not "values" in json else json["values"]

    def to_dict(self):
        json = {}
        json["name"] = self.name
        json["values"] = self.values
        return json

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiTimeSeriesCollection:
    def __init__(self, json):
        self.values = [ApiTimeSeries(p) for p in json]

    def to_dict(self):
        return [p.to_dict() for p in self.values]

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiReportEpisode:
    def __init__(self, json):
        self.name = json["name"]
        self.series = ApiTimeSeriesCollection(json["series"])

    def to_dict(self):
        json = {}
        json["name"] = self.name
        json["series"] = self.series.to_dict() if self.series is not None else None
        return json

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiReportEpisodeCollection:
    def __init__(self, json):
        self.values = [ApiReportEpisode(p) for p in json]

    def to_dict(self):
        return [p.to_dict() for p in self.values]

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiReportData:
    def __init__(self, json):
        self.episodes = ApiReportEpisodeCollection(json["episodes"])
        self.timeStamps = None if not "timeStamps" in json else json["timeStamps"]

    def to_dict(self):
        json = {}
        json["episodes"] = self.episodes.to_dict() if self.episodes is not None else None
        json["timeStamps"] = self.timeStamps
        return json

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiReportDataCollection:
    def __init__(self, json):
        self.values = [ApiReportData(p) for p in json]

    def to_dict(self):
        return [p.to_dict() for p in self.values]

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class RunDetails:
    def __init__(self, json):
        self.progress = json["progress"]
        self.status = ApiStepSeriesCollection(json["status"])

    def to_dict(self):
        json = {}
        json["progress"] = self.progress
        json["status"] = self.status.to_dict() if self.status is not None else None
        return json

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class RunDetailsCollection:
    def __init__(self, json):
        self.values = [RunDetails(p) for p in json]

    def to_dict(self):
        return [p.to_dict() for p in self.values]

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiStepSeries:
    def __init__(self, json):
        self.name = json["name"]
        self.steps = None if not "steps" in json else json["steps"]
        self.values = None if not "values" in json else json["values"]

    def to_dict(self):
        json = {}
        json["name"] = self.name
        json["steps"] = self.steps
        json["values"] = self.values
        return json

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

class ApiStepSeriesCollection:
    def __init__(self, json):
        self.values = [ApiStepSeries(p) for p in json]

    def to_dict(self):
        return [p.to_dict() for p in self.values]

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    def to_pandas(self):
        return pd.json_normalize(self.to_dict())

    def __str__(self):
        return str(self.to_pandas())

    def to_json(self):
        return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)

    def _repr_html_(self):
         return self.to_pandas()._repr_html_()

