#%%
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from pathlib import Path
import uuid
import tensorflow as tf
from hps.rl.builders.rl_builder import RlBuilder
import numpy as np
from hps.rl.logging.tensorboard_logger import TensorboardLogger
from hps.rl.logging.agent_plugin import CompositePlugin, ConsoleLogger
import os

from hps.rl.settings import RunSettings, AgentSettings

from server.namegenerator import get_random_name

import cProfile, pstats, io
from pstats import SortKey  # type: ignore


use_gpu = False
if not use_gpu:
    tf.config.set_visible_devices([], 'GPU')
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

np.random.seed()

run_settings = RunSettings()

run_settings.system = "small"
run_settings.uid = str(uuid.uuid4())
run_settings.train_intervals = run_settings.eval_intervals = 52
run_settings.train_episodes = 20000
run_settings.forecast_id = 7

agent_settings = run_settings.agent_settings[0]
agent_settings.name = get_random_name()

base_dir = str(Path.home()/Path("hps_server/{}/" + run_settings.uid + "/" + agent_settings.name))

agent_settings.output_checkpoint_folder = base_dir.format("checkpoints")
agent_settings.start_checkpoint_folder = None # "/home/janik/hps_server/checkpoints/849a1b0d-699d-451a-b612-0c3b1c62ecf0/Blissful_Ramanujan"

agent_settings.seed = np.random.randint(100, 300)

print("RUN", agent_settings.seed, agent_settings.name)

log_dir = base_dir.format("tb_logs")
    
plugin = CompositePlugin([
    TensorboardLogger(log_dir=log_dir, run_settings=run_settings) , ConsoleLogger()
])

rl_builder = RlBuilder(run_settings, agent_settings)
agent_runner = rl_builder.build(plugin)

pr = cProfile.Profile()
pr.enable()
agent_runner.run()

pr.disable()
s = io.StringIO()
sortby = SortKey.CUMULATIVE
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())