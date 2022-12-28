"""Script for running HydroRL without using the API."""
#%%
import sys, os
from pathlib import Path
#sys.path.insert(1, os.path.join(sys.path[0], '..'))
sys.path.insert(0, str(Path.home()/Path("gitsource/HydroScheduling")))

# from server.gpu_init import per_process_gpu_init
# per_process_gpu_init()
from core.noise import Noise

# import tensorflow as tf
from pathlib import Path
import uuid

from hps.rl.builders.rl_builder import RlBuilder
import numpy as np
# from hps.rl.logging.tensorboard_logger import TensorBoardTuningLogger, TensorboardTrainLogger
from hps.rl.logging.agent_plugin import CompositePlugin, ConsoleLogger
import os
from datetime import datetime as dt

from hps.rl.settings import RunSettings, AgentSettings
from server.namegenerator import get_random_name
from sqlalchemy import desc
from server.db_connection import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from server.model import Forecast, HydroSystem, Project, ProjectRun, ProjectRunStartVolume, Reservoir
import random as rand

SEED = 120
def set_seeds(seed):
    os.environ['PYTHONHASHSEED'] = str(seed)
    rand.seed(seed)
    # tf.random.set_seed(seed)
    np.random.seed(seed)


def set_global_determinism(seed):
    set_seeds(seed)

    # os.environ['TF_DETERMINISTIC_OPS'] = '1'
    # os.environ['TF_CUDNN_DETERMINISTIC'] = '1'
    
    # tf.config.threading.set_inter_op_parallelism_threads(1)
    # tf.config.threading.set_intra_op_parallelism_threads(1)

# Call the above function with seed value
set_global_determinism(seed=SEED)

SEED = 120

system_name = "System"
project_name = "Renaissance project II"
run_name = "Test run"
forecast_name = "NVE+Spot+Smoothing"

np.random.seed()
run_settings = RunSettings()
run_settings.n_clusters = 7
run_settings.reward_scale_factor = 1
run_settings.uid = str(uuid.uuid4())
run_settings.train_intervals = run_settings.eval_intervals = int(24/3*7*2*3)
run_settings.train_step_frequency = run_settings.eval_step_frequency = '3H'
run_settings.use_linear_model = False
run_settings.train_episodes = 200
run_settings.trains_per_episode = 3
run_settings.observation_settings.global_max_price = 150 # [m.u./MWh] # Values above will be clipped in observation space
run_settings.observation_settings.include_end_vol = False
run_settings.observation_settings.include_flow = True
run_settings.observation_settings.include_lin = True
run_settings.observation_settings.include_seasonal_cosine_time = False
run_settings.observation_settings.price_steps = 1
run_settings.observation_settings.num_trig = 0
run_settings.sample_with_noise = Noise.White # "W": White noise (N(0,1)), "S": Std.dev. of clusters, None: No noise

agent_settings = run_settings.agent_settings[0]
agent_settings.name = get_random_name()
agent_settings.seed = 120 #np.random.randint(100, 300)
agent_settings.episodes_to_initially_collect = 100
agent_settings.eval_episodes = 1
agent_settings.eval_interval = 20
agent_settings.episodes_stored_in_buffer = 1000
agent_settings.batch_size = 256

run_settings.sac_settings.target_update_tau = 0.001
run_settings.sac_settings.target_update_period = 1

base_dir = str(Path.home()/Path("hps_server/{}/" + agent_settings.name))

agent_settings.output_checkpoint_folder = base_dir.format("checkpoints")

print("RUN", agent_settings.seed, agent_settings.name)

engine = create_engine()
Session = sessionmaker(bind=engine)
session = Session()

[f.Name for f in session.query(Forecast).all()]
hydro_system = session.query(HydroSystem).filter_by(Name=system_name).first()

if hydro_system is None:
    raise ValueError("Unknown hydro system {}".format(hydro_system))

project = session.query(Project).filter_by(Name=project_name).first()

if project is None:
    project = Project(Name=project_name, HydroSystemId=hydro_system.HydroSystemId, ProjectUid = str(uuid.uuid4()))
    session.add(project)
    session.commit()

forecast = session.query(Forecast).filter_by(Name=forecast_name, HydroSystemId=hydro_system.HydroSystemId).first()

project_run = ProjectRun(ProjectRunGuid=str(uuid.uuid4()), ProjectId=project.ProjectId, 
    StartTime = str(dt.now()), ForecastId=forecast.ForecastId, Settings="", ApiSettings="", Comment=run_name, EvaluatedOn=None, PreviousProjectRunId=None, PreviousQValueProjectRunId=None)

session.add(project_run)
session.commit()

ress = session.query(Reservoir).filter_by(HydroSystemId=hydro_system.HydroSystemId).all()

for res in ress:
    sv = ProjectRunStartVolume(ProjectRunId=project_run.ProjectRunId, ReservoirId=res.ReservoirId, Value=res.MaxVolume*0.01)
    session.add(sv)

session.commit()

rl_builder = RlBuilder(run_settings, agent_settings, project_run)

tb_log_dir = str(Path.home()/Path("hps_server/armageddon/tb_logs/")) + "/" + project.Name + "/" + agent_settings.name
h_params = None
plugin = CompositePlugin([
     ConsoleLogger()
])

rl_builder = RlBuilder(run_settings, agent_settings, project_run)
agent_runner = rl_builder.build(plugin)
# train_plugin = TensorboardTrainLogger(log_dir=tb_log_dir, run_settings=run_settings)

