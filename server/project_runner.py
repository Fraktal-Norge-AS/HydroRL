from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker

from model import Project, Agent, ProjectRun, AgentControl, ProjectRunControl
from server.db_connection import create_engine
import numpy as np
import copy

from agent_executor import execute_agent
from hps.rl.settings import RunSettingsSerializer
from appsettings import appSettings
from server.namegenerator import get_random_names
from setting_combiner import SettingsCombiner
from multiprocessing import Process
from datetime import datetime as dt
from datetime import timedelta as td
import time

NUM_AGENTS = 5

AgentsTerminated = -2
SleepComplete = -1
Terminate = 0
SpawnBestWithBuffer = 1
SpawnBestNoBuffer = 2
ControlAcc = 10


class ProjectRunner:
    def __init__(self, project_guid, run_id):
        self.engine = create_engine()
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.project = self.session.query(Project).filter_by(ProjectUid=project_guid).first()
        self.active_agents = {}

        self.project_run = self.session.query(ProjectRun).filter_by(ProjectRunId=run_id).first()

        self.project_run.StartTime = str(dt.now())
        self.session.commit()

        combinder = SettingsCombiner(self.session)
        self.run_settings, settings_modified = combinder.combine_settings(self.project_run)
        self.agent_count = len(self.run_settings.agent_settings)

        if settings_modified:
            self.project_run.Settings = RunSettingsSerializer.serialize(self.run_settings)
            self.session.add(self.project_run)
            self.session.commit()

    def SurvivalOfTheFittest(self, keep_buffer):
        """Spawn new agents from the current best.

        :param keep_buffer: Whether to keep the replay buffer or not
        :type keep_buffer: Bool
        """
        agents = self.session.query(Agent).filter_by(ProjectRunId=self.project_run.ProjectRunId, EndTime=None)

        current_best_agent = agents[0]
        current_best_value = agents[0].BestStepValue
        for agent in agents[1:]:
            if agent.BestStepValue > current_best_value:
                current_best_value = agent.BestStepValue
                current_best_agent = agent

        best_agent_id = current_best_agent.AgentId

        for a in agents:
            if a.AgentId == best_agent_id:
                continue
            killmsg = AgentControl(AgentId=a.AgentId, Signal=1)
            self.session.add(killmsg)
            del self.active_agents[a.AgentUid]

        _, a_settings = self.active_agents[current_best_agent.AgentUid]

        new_settings = self.spawn_agent(self.agent_count - 1, a_settings, keep_buffer)

        index_offset = len(self.run_settings.agent_settings)

        # Update settings of projectrun
        self.run_settings.agent_settings += new_settings
        ser_settings = RunSettingsSerializer.serialize(self.run_settings)
        self.session.query(ProjectRun).filter_by(ProjectRunId=self.project_run.ProjectRunId).update(
            {"Settings": ser_settings}
        )

        self.session.commit()

        self.start_agents(new_settings, index_offset, 0, best_agent_id)

    def get_fresh_seeds(self, count: int) -> np.ndarray:
        return np.array(100) + np.random.choice(500, size=count, replace=False)

    def spawn_agent(self, count, from_agent_settings, keep_buffer):
        new_agent_settings = []
        fresh_seeds = self.get_fresh_seeds(count)

        for i in range(count):
            a_settings = copy.deepcopy(from_agent_settings)
            a_settings.seed = fresh_seeds[i]
            a_settings.start_checkpoint_folder = from_agent_settings.output_checkpoint_folder
            a_settings.keep_buffer_from_start_checkpoint = keep_buffer
            a_settings.name = self.run_settings.spare_agent_names[0]
            a_settings.reset_global_step = False  # Continue with current global step
            self.run_settings.spare_agent_names = self.run_settings.spare_agent_names[1:]

            new_agent_settings.append(a_settings)

        return new_agent_settings

    def terminate_all_agents(self):
        agents = self.session.query(Agent).filter_by(ProjectRunId=self.project_run.ProjectRunId, EndTime=None)
        for a in agents:
            killmsg = AgentControl(AgentId=a.AgentId, Signal=1)
            self.session.add(killmsg)
        self.session.commit()

    def sleepUntilSignal(self, sleep_seconds):

        end_time = dt.now() + td(seconds=sleep_seconds)

        while end_time > dt.now():
            control = (
                self.session.query(ProjectRunControl)
                .filter(ProjectRunControl.ProjectRunId == self.project_run.ProjectRunId)
                .order_by(ProjectRunControl.ProjectRunControlId.desc())
                .first()
            )
            if control is not None and control.Signal != ControlAcc:
                print("Control signal received ", control.Signal)
                acc = ProjectRunControl(ProjectRunId=self.project_run.ProjectRunId, Signal=ControlAcc)
                self.session.add(acc)
                self.session.commit()
                return control.Signal
            active_agent = (
                self.session.query(Agent).filter_by(ProjectRunId=self.project_run.ProjectRunId, EndTime=None).first()
            )
            if active_agent is None:
                print("Agents terminated ", AgentsTerminated)
                return AgentsTerminated

            time.sleep(1)

        return SleepComplete

    def start_agents(self, agent_settings, start_index, step_offset, parent_id):
        for i, a_settings in enumerate(agent_settings):
            args = (self.project.ProjectUid, self.project_run.ProjectRunId, i + start_index, step_offset, parent_id)
            p = Process(target=execute_agent, args=args)
            self.active_agents[a_settings.name] = (p, a_settings)
            p.start()

    def start(self):
        self.start_agents(self.run_settings.agent_settings, 0, 0, None)

        # Allow processes to start
        time.sleep(10)

        termianted = False
        while not termianted:
            try:
                signal = self.sleepUntilSignal(5)
                if signal == AgentsTerminated:
                    termianted = True
                elif signal == Terminate:
                    self.terminate_all_agents()
                    termianted = True
                elif signal == SpawnBestNoBuffer or signal == SpawnBestWithBuffer:
                    self.SurvivalOfTheFittest(signal == SpawnBestWithBuffer)

            except Exception as e:
                print(e)

        print("Joining agents")

        for p, s in self.active_agents.values():
            p.join()

        print("All agents joined")

        self.project_run.EndTime = str(dt.now())
        self.session.commit()

        print("Successfully terminated")


def run_project(projectGuid, run_id):
    runner = ProjectRunner(projectGuid, run_id)
    runner.start()


def start_run_project(projectGuid, run_id):
    p = Process(target=run_project, args=(projectGuid, run_id))
    p.start()
