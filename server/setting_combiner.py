from enum import Enum

from hps.rl.environment.end_value_type import EndStateIncentive

from server.model import Agent, ProjectRun
from hps.rl.settings import RunSettings, RunSettingsSerializer
from server.namegenerator import get_random_names
from server.appsettings import appSettings
import json
import numpy as np


class StepResolution(str, Enum):
    Week = "Week"
    Day = "Day"
    Hour = "Hour"


class SettingsCombiner:
    def __init__(self, session):
        self.session = session

    def get_best_folder(self, run_uid):
        prev_run = self.session.query(ProjectRun).filter(ProjectRun.ProjectRunGuid == run_uid).first()
        best_agent = (
            self.session.query(Agent)
            .filter(Agent.ProjectRunId == prev_run.ProjectRunId)
            .order_by(Agent.BestStepValue.desc())
            .first()
        )
        agent = self.session.query(Agent).filter_by(AgentId=best_agent.AgentId).first()
        return agent.BestModelPath

    def combine_settings(self, project_run):

        run_settings = None
        is_modified = False
        if project_run.Settings is not None:
            run_settings = RunSettingsSerializer.deserialze(project_run.Settings)
        else:
            run_settings = RunSettings()

            # Ensure basic settings
            run_settings.uid = project_run.ProjectRunGuid
            run_settings.train_episodes = 1000
            agent_count = len(run_settings.agent_settings)
            seeds = (100 + np.random.choice(500, size=agent_count, replace=False)).astype(int)
            names = get_random_names(agent_count * 10)
            for i, agent in enumerate(run_settings.agent_settings):
                agent.seed = seeds[i]
                agent.name = names[i]
                agent.output_checkpoint_folder = appSettings.get_checkpoint_folder(run_settings.uid, agent.name)
            run_settings.spare_agent_names = names[agent_count:]
            run_settings.system = project_run.Project.HydroSystem.Name
            is_modified = True

        if project_run.ApiSettings is not None:
            api_settings = json.loads(project_run.ApiSettings)
            run_settings.discount_rate = float(api_settings["discountRate"])
            run_settings.train_episodes = int(api_settings["trainEpisodes"])
            run_settings.end_state_incentive = api_settings["endStateIncentive"]
            run_settings.sample_with_noise = api_settings["noise"]
            run_settings.randomize_init_vol = bool(api_settings["randomizeStartVolume"])
            run_settings.reward_scale_factor = float(api_settings["rewardScaleFactor"])
            run_settings.n_clusters = int(api_settings["forecastClusters"])
            run_settings.price_of_spillage = float(api_settings["priceOfSpillage"])
            run_settings.agent_algorithm = api_settings["agentAlgorithm"]

            for i, agent in enumerate(run_settings.agent_settings):
                agent.eval_episodes = int(api_settings["evaluationEpisodes"])
                agent.eval_interval = int(api_settings["evaluationInterval"])

            run_settings.eval_intervals = run_settings.train_intervals = int(api_settings["stepsInEpisode"])
            step_frequency = str(api_settings["stepFrequency"])
            if api_settings["stepResolution"] == StepResolution.Week:
                step_frequency += "W"
            elif api_settings["stepResolution"] == StepResolution.Day:
                step_frequency += "D"
            elif api_settings["stepResolution"] == StepResolution.Hour:
                step_frequency += "H"
            else:
                raise ValueError(
                    f"Invalid value {api_settings['stepResolution']} for stepResolution. Must be either 'Week' or 'Day'."
                )
            run_settings.train_step_frequency = run_settings.eval_step_frequency = step_frequency

            # Read checkpoint folders
            start_folder = None
            q_value_folder = None
            if api_settings["previousProjectRunUid"]:
                start_folder = self.get_best_folder(api_settings["previousProjectRunUid"])

            if run_settings.end_state_incentive == EndStateIncentive.QValue:
                q_value_folder = self.get_best_folder(api_settings["previousQValueProjectRunUid"])

            for agent in run_settings.agent_settings:
                agent.start_checkpoint_folder = start_folder
                agent.q_value_checkpoint_folder = q_value_folder

            if run_settings.end_state_incentive == EndStateIncentive.ProvidedEndEnergyPrice:
                run_settings.end_energy_price = float(api_settings["endEnergyPrice"])

            is_modified = True

        return run_settings, is_modified
