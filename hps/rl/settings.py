import json
from typing import Optional, List
import numpy as np
from hps.rl.environment.end_value_type import EndStateIncentive
from core.markov_chain import Noise

from enum import Enum


class AgentAlgorithm(str, Enum):
    SAC = "SAC"
    A2C = "A2C"
    DDPG = "DDPG"
    TD3 = "TD3"
    PPO = "PPO"


class NetworkSettings:
    """
    Settings applied to the networks.

    :var structure: List representing the hidden layers in the network.
    :var learning_rate: Learning rate used by the network optimizer.
    :var learning_rate_decay: Used if the optimizer is RMSProp.
    :var optimizer: Name of the optimizer.
    """

    def __init__(self):
        self.structure = [256, 256]
        self.learning_rate = 4e-3
        self.learning_rate_decay = 0.99
        self.optimizer = "Adam"


class ObservationSettings:
    def __init__(self):
        self.include_vol = True
        self.include_end_vol = False
        self.include_flow = True
        self.include_lin = True
        self.include_different_time_lengths = False
        self.include_seasonal_linear_time = False
        self.include_seasonal_cosine_time = False
        self.num_sectors = 0
        self.price_steps = 1
        self.num_trig = 0
        self.global_max_price: Optional[float] = None  # [m.u./MWh] # Values above will be clipped in observation space
        self.global_max_inflow: Optional[float] = None  # [m3/s] Values above will be clipped in observation space
        self.log_normalize_price_scaler = False  # --SB-- : seems to have no measurable effect
        self.include_weekday_bins = False
        self.include_hourly_bins = False
        self.hourly_bin_interval = 3
        self.time_periods: Optional[List] = [24, 24 * 7]  # If adding fourier feature extractor


class SacSettings:
    def __init__(self):
        self.actor = NetworkSettings()
        self.critic = NetworkSettings()
        self.alpha = NetworkSettings()
        self.target_update_period = 1
        self.target_update_tau = 0.005
        self.target_entropy = None
        self.gradient_clipping = 10.0


class AgentSettings:
    def __init__(self):
        self.name = ""  # Agent name , unique for a run
        self.seed = None # type: Optional[int] # Random seed
        self.eval_interval = 30  # Interval for evaluation
        self.eval_episodes = 5  # Number of episodes used for evaluation
        self.episodes_to_initially_collect = 40
        self.episodes_stored_in_buffer = 500  # Values around 25-50
        self.batch_size = 256  # Of the tf.dataset
        self.start_checkpoint_folder = None  # Provides network states to start training from
        self.q_value_checkpoint_folder = None  # Provides critic networs to use as end q-value
        self.output_checkpoint_folder = None # type: Optional[str]
        self.reset_global_step = True


class RunSettings:
    def __init__(self):
        self.uid = ""
        self.train_episodes = 10000
        self.trains_per_episode = 3
        self.system = None
        self.n_clusters = 7
        self.train_intervals = 104  # [56, 100]
        self.train_step_frequency = "7D"  # ['3H', '7D']
        self.eval_intervals = 104  # [56, 100]
        self.eval_step_frequency = "7D"  # ['3H', '7D']
        self.use_linear_model = False
        self.forecast_sampling_seed = 42
        self.start_volumes = None
        self.end_state_incentive = EndStateIncentive.MeanEnergyPrice
        self.randomize_init_vol = True
        self.spare_agent_names = None
        self.agent_settings = [AgentSettings() for _ in range(4)]
        self.observation_settings = ObservationSettings()
        self.sac_settings = SacSettings()
        self.discount_rate = 0.04
        self.reward_scale_factor = 10
        self.price_scale_factor = 1
        self.end_energy_price = None
        self.price_of_spillage = 0.0  # [EUR/MWh]
        self.sample_with_noise = (
            Noise.Off
        )  # "White": White noise (N(0,1)), "Standard dev": Std.dev. of clusters, Off: No noise
        self.ensure_determinism = False  # Note that setting this flag to True this will reduce performance
        self.use_shared_replay_buffer = False
        self.agent_algorithm = AgentAlgorithm.SAC
        self.log_to_tensorboard = True
        self.log_replay_buffer_when_finished = True


class SettingsEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (np.number, np.ndarray)):
            return o.tolist()
        elif isinstance(o, complex):
            return [o.real, o.imag]
        elif isinstance(o, set):
            return list(o)
        elif isinstance(o, bytes):
            return o.decode()
        elif isinstance(o, np.bool_):
            return bool(o)
        elif isinstance(o, bool):
            return int(o)
        else:
            key = "__{}__".format(o.__class__.__name__)
            dictionary = o.__dict__
            return {key: dictionary}


class RunSettingsSerializer:
    def serialize(settings):
        return json.dumps(settings, cls=SettingsEncoder)

    def object_hook(o):
        obj = None
        if "__NetworkSettings__" in o:
            obj = NetworkSettings()
            obj.__dict__.update(o["__NetworkSettings__"])
        elif "__AgentSettings__" in o:
            obj = AgentSettings()
            obj.__dict__.update(o["__AgentSettings__"])
        elif "__RunSettings__" in o:
            obj = RunSettings()
            obj.__dict__.update(o["__RunSettings__"])
        elif "__SacSettings__" in o:
            obj = SacSettings()
            obj.__dict__.update(o["__SacSettings__"])
        elif "__ObservationSettings__" in o:
            obj = ObservationSettings()
            obj.__dict__.update(o["__ObservationSettings__"])

        if obj is not None:
            return obj
        return o

    def deserialze(json_text):
        deserialized = json.loads(json_text, object_hook=RunSettingsSerializer.object_hook)
        return deserialized
