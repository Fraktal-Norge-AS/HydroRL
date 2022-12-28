#%%

from core.noise import Noise
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import multiprocessing
multiprocessing.set_start_method('fork', True)

from tensorboard.plugins.hparams import api as hp
from pathlib import Path
from datetime import datetime
import uuid

from hps.rl.builders.rl_builder import RlBuilder
import numpy as np
from hps.rl.logging.tensorboard_logger import TensorBoardTuningLogger
import os

from hps.rl.settings import RunSettings
from server.namegenerator import get_random_name

from multiprocessing import Process

class ParameterGenerator:

    def __init__(self, net_structure_id, seed, forecast_id, net_structure_count = 10):
        self.parameters = []

        TARGET_UPDATE_PERIOD = hp.HParam(
            'target_update_period', hp.Discrete([1])) # keep 1 discard 4
        TARGET_UPDATE_TAU = hp.HParam(
            'target_update_tau', hp.Discrete([0.001])) # keep 0.001, higher gives worse results, should we try lower?
        LEARNING_RATE = hp.HParam(
            'learning_rate', hp.Discrete([5e-4])) # 3e-3 for adam, 1e-3 to 5e-4 for rmsProp
        REWARD_SCALE_FACTOR = hp.HParam(
            'reward_scale_factor', hp.Discrete([50])) # keep one for now, should be explored more, may not matter much? Very important according to paper.
        PRICE_SCALE_FACTOR = hp.HParam(
            'price_scale_factor', hp.Discrete([2])) 
        GRADIENT_CLIPPING = hp.HParam(
            'gradient_clipping', hp.Discrete([5.0])) # keep one for now, should be explored more .5 and 2. also give decent results
        NET_CONFIG_ID = hp.HParam(
            'net_configuration', hp.Discrete([i + 1 for i in range(net_structure_count)]))
        SEED = hp.HParam(
            'seed', hp.Discrete([seed]))
        EPISODES_STORED_IN_BUFFER  = hp.HParam(
            'episodes_stored_in_buffer', hp.Discrete([500])) # [25, 50]
        RANDOMIZE_INIT_VOLUME = hp.HParam(
            'randomize_init_volume', hp.Discrete([True]))
        BATCH_SIZE = hp.HParam(
            'batch_size', hp.Discrete([312]))
        FORECAST_ID = hp.HParam(
            'forecast_id', hp.Discrete([forecast_id]))

        for target_update_period in TARGET_UPDATE_PERIOD.domain.values:
            for target_update_tau in TARGET_UPDATE_TAU.domain.values:
                for price_scale_factor in PRICE_SCALE_FACTOR.domain.values:
                    for reward_scale_factor in REWARD_SCALE_FACTOR.domain.values:                    
                        for gradient_clipping in GRADIENT_CLIPPING.domain.values:
                            for learning_rate in LEARNING_RATE.domain.values:
                                for episodes_stored_in_buffer in EPISODES_STORED_IN_BUFFER.domain.values:
                                    for randomize_init_volume in RANDOMIZE_INIT_VOLUME.domain.values:
                                        for batch_size in BATCH_SIZE.domain.values:

                                            hparams = {
                                                TARGET_UPDATE_PERIOD: target_update_period, 
                                                TARGET_UPDATE_TAU: target_update_tau,
                                                LEARNING_RATE : learning_rate,
                                                PRICE_SCALE_FACTOR: price_scale_factor,
                                                REWARD_SCALE_FACTOR : reward_scale_factor,
                                                GRADIENT_CLIPPING : gradient_clipping,
                                                NET_CONFIG_ID : net_structure_id,
                                                SEED : seed,
                                                EPISODES_STORED_IN_BUFFER: episodes_stored_in_buffer,
                                                RANDOMIZE_INIT_VOLUME: randomize_init_volume,
                                                BATCH_SIZE: batch_size,
                                                FORECAST_ID: forecast_id
                                            }

                                            self.parameters.append((
                                                target_update_period, target_update_tau, learning_rate, price_scale_factor,
                                                reward_scale_factor, gradient_clipping, episodes_stored_in_buffer,
                                                randomize_init_volume, batch_size, forecast_id, seed, hparams
                                            ))
            

    def get_params(self, idx):
        return self.parameters[idx]

    def length(self):
        return len(self.parameters)


def execute_agent():
    import tensorflow as tf

    use_gpu = False
    if not use_gpu:
        tf.config.set_visible_devices([], 'GPU')
        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    np.random.seed()

    run_settings = RunSettings()

    run_settings.n_clusters = 1
    run_settings.uid = str(uuid.uuid4())
    run_settings.train_episodes = 10000
    run_settings.trains_per_episode = 3    
    run_settings.observation_settings.global_max_price = 150 # [m.u./MWh] # Values above will be clipped in observation space
    run_settings.observation_settings.include_end_vol = True
    run_settings.observation_settings.include_flow = True
    run_settings.observation_settings.include_lin = True
    run_settings.observation_settings.price_steps = 1
    run_settings.observation_settings.num_trig = 0
    run_settings.sample_with_noise = Noise.White

    agent_settings = run_settings.agent_settings[0]
    agent_settings.name = get_random_name()
    agent_settings.eval_interval = 500

    base_dir = str(Path.home()/Path("hps_server/{}/" + run_settings.uid + "/" + agent_settings.name))
    agent_settings.output_checkpoint_folder = base_dir.format("checkpoints")

    network_structure, network_structure_id = [64, 64, 32, 32], 1
    seed = np.random.randint(100, 300)
    forecast_id = 416  # 419: medium
    param_gen = ParameterGenerator(network_structure_id, seed, forecast_id=forecast_id, net_structure_count=1)

    for idx in range(param_gen.length()):
        params = param_gen.get_params(idx)
        target_update_period = params[0]
        target_update_tau = params[1]
        learning_rate = params[2]
        price_scale_factor = params[3]
        reward_scale_factor = params[4]
        gradient_clipping = params[5]
        episodes_stored_in_buffer = params[6]
        randomize_init_volume = params[7]
        batch_size = params[8]
        forecast_id = params[9]        
        seed = params[10]
        h_params = params[-1]
        print({h.name: h_params[h] for h in h_params})
        
        run_settings.sac_settings.target_update_period = target_update_period
        run_settings.sac_settings.target_update_tau = target_update_tau
        run_settings.sac_settings.actor.learning_rate = learning_rate
        run_settings.sac_settings.critic.learning_rate = learning_rate
        run_settings.sac_settings.alpha.learning_rate = learning_rate
        run_settings.sac_settings.gradient_clipping = gradient_clipping
        
        run_settings.price_scale_factor = price_scale_factor
        run_settings.reward_scale_factor = reward_scale_factor
        run_settings.randomize_init_vol = randomize_init_volume
        run_settings.forecast_id = forecast_id

        agent_settings.episodes_stored_in_buffer = episodes_stored_in_buffer
        agent_settings.batch_size = batch_size
        agent_settings.seed = seed

        train_log_dir = str(
                Path.home()/Path(
                    "hps_server/tb_logs_apex2/hp_tuning/" + agent_settings.name + "_" 
                    + "/seed_" + str(agent_settings.seed)
                    + "_" + datetime.now().strftime("%Y%m%d-%H%M%S")
                )
            )
        tf.keras.backend.clear_session()
        rl_builder = RlBuilder(run_settings, agent_settings)
        plugin = TensorBoardTuningLogger(log_dir=train_log_dir, run_settings=run_settings, h_params=h_params)
        agent_runner = rl_builder.build(plugin)
        agent_runner.run()

        print(f"ITERATION {idx+1}")

def run_grid_search():
    active_agents = []
        
    for _ in range(5):
        p = Process(target=execute_agent)
        active_agents.append(p)
        p.start()
        
    for p in active_agents:
        p.join()

    print("agents joined")
