from gpu_init import per_process_gpu_init

per_process_gpu_init()

from hps.rl.builders.rl_builder import RlBuilder
from hps.rl.agent_runner import AgentRunner
from sqlalchemy import desc
from server.db_connection import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from model import Project, Agent, AgentControl, ProjectRun
import uuid
from datetime import datetime as dt
from server.namegenerator import get_random_name
from db_logger import DbLogger

import numpy as np
import os
import json
from jsonEncoder import JsonEncoder
from appsettings import appSettings
from hps.rl.settings import AgentSettings, RunSettingsSerializer, RunSettings
import time
import tensorflow as tf

TERMINATE_CHECK_INTERVAL = 2


class AgentExecutor:
    def __init__(self, project_guid, project_run_id, agent_index, step_offset, parent_id):

        np.random.seed()

        self.engine = create_engine()
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.project = self.session.query(Project).filter_by(ProjectUid=project_guid).first()

        self.project_run = self.session.query(ProjectRun).filter_by(ProjectRunId=project_run_id).first()
        self.settings: RunSettings = RunSettingsSerializer.deserialze(self.project_run.Settings)
        self.agent_settings: AgentSettings = self.settings.agent_settings[agent_index]

        self.run_id = project_run_id

        self.agent_name = get_random_name()

        self.best_model_path = self.agent_settings.output_checkpoint_folder
        self.agent = Agent(
            ProjectId=self.project.ProjectId,
            ProjectRunId=self.run_id,
            AgentUid=self.agent_settings.name,
            Seed=self.agent_settings.seed,
            BestModelPath=self.best_model_path,
            StartTime=str(dt.now()),
            Ancestor=parent_id,
        )

        self.start_model_path = None
        if parent_id is not None:
            parent_agent = self.session.query(Agent).filter_by(AgentId=parent_id).first()
            self.start_model_path = parent_agent.BestModelPath

        self.session.add(self.agent)
        self.session.commit()
        self.step_offset = step_offset
        self.last_terminate_check_time = None

        self.db_logger = DbLogger(self.session, self.agent.AgentId, project_run_id, "scalars", "plot")

    def should_terminate(self):
        if self.last_terminate_check_time is None:
            self.last_terminate_check_time = time.time()
        else:
            now_time = time.time()
            time_since_last = now_time - self.last_terminate_check_time

            if time_since_last >= TERMINATE_CHECK_INTERVAL:
                control = (
                    self.session.query(AgentControl)
                    .filter_by(AgentId=self.agent.AgentId)
                    .order_by(AgentControl.AgentControlId.desc())
                    .first()
                )
                self.last_terminate_check_time = now_time
                return control is not None
        return False

    def log_info(
        self,
        step,
        eval_env,
        returns,
        avg_return,
        currentbest,
        new_best,
        rewards,
        end_rewards,
        train_metrics,
        train_loss,
        q_value_tuple,
        q_value,
        alpha,
        network_weights,
    ):
        step += self.step_offset
        self.db_logger.log_info(
            step,
            eval_env,
            returns,
            avg_return,
            currentbest,
            new_best,
            rewards,
            end_rewards,
            train_metrics,
            train_loss,
            q_value_tuple,
            q_value,
        )

        if new_best["eval"]:
            self.agent.BestStep = step
            self.agent.BestStepValue = avg_return
            self.session.commit()

    def get_best_step(self):
        return self.agent.BestStep

    def log_initial_values(self, eval_env):
        pass

    def log_eval_episode(self, step, episode_name, eval_env):
        self.db_logger.log_eval_episode(step, episode_name, eval_env)

    def run(self):
        self.settings.train_episodes = self.settings.train_episodes - self.step_offset

        rl_builder = RlBuilder(self.settings, self.agent_settings, self.project_run)
        runner = rl_builder.build(self)
        runner.run()

        end_time = str(dt.now())
        self.db_logger.terminate_series(end_time)
        self.agent.EndTime = end_time
        self.session.commit()

    def log_h_params(self, h_params):
        pass


def execute_agent(project_guid, project_run_id, agent_index, step_offset, parent_id):
    executor = AgentExecutor(project_guid, project_run_id, agent_index, step_offset, parent_id)
    executor.run()
