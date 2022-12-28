from sqlalchemy.orm import sessionmaker
from server.db_connection import create_engine
from model import ProjectRun

from setting_combiner import SettingsCombiner

from hps.rl.settings import RunSettingsSerializer
from hps.rl.builders.rl_builder import RlBuilder
from appsettings import appSettings
from db_logger import DbLogger

from multiprocessing import Process
from datetime import datetime as dt


class Evaluator:
    def __init__(self, eval_id):
        self.engine = create_engine()
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.project_run = self.session.query(ProjectRun).filter_by(ProjectRunGuid=eval_id).first()
        self.project_run.StartTime = str(dt.now())
        self.session.commit()

        combinder = SettingsCombiner(self.session)
        self.settings, settings_modified = combinder.combine_settings(self.project_run)
        self.agent_settings = self.settings.agent_settings[0]
        self.agent_settings.start_checkpoint_folder = self.project_run.Agent.BestModelPath
        if settings_modified:
            self.project_run.Settings = RunSettingsSerializer.serialize(self.settings)
            self.session.add(self.project_run)
            self.session.commit()

        self.db_logger = DbLogger(
            self.session, self.project_run.EvaluatedOn, self.project_run.ProjectRunId, None, "eplots", log_steps=False
        )

    def should_terminate(self):
        return False

    def log_h_params(self, h_params):
        pass

    def log_info(
        self,
        step,
        eval_env,
        returns,
        sum_return,
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
        pass

    def log_initial_values(self, eval_env):
        pass

    def log_eval_episode(self, step, episode_name, eval_env):
        self.db_logger.log_eval_episode(1, episode_name, eval_env)

    def run(self):
        self.settings.train_episodes = 0

        rl_builder = RlBuilder(self.settings, self.agent_settings, self.project_run)
        runner = rl_builder.build(self)

        current_best = {"eval": -1e10, "train": -1e10}

        current_best = runner.evaluate(1, current_best, None)
        print(current_best)

        end_time = str(dt.now())
        self.db_logger.terminate_series(end_time)
        self.project_run.EndTime = end_time
        self.session.commit()
        print("EVAL COMPLETE")


def run_evaluation(eval_id):
    runner = Evaluator(eval_id)
    runner.run()


def start_evalaution(eval_id):
    p = Process(target=run_evaluation, args=(eval_id,))
    p.start()
