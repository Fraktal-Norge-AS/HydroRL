import numpy as np
from typing import Callable
import os

from hps.rl.environment.hsenvironment import HSEnvironment
from hps.rl.sac.time_feature_extractor import (
    TimeFourierFeatureExtractor,
    CustomCombinedExtractor,
    CombinedIdentityExtractor,
)
from hps.rl.environment.observations_generator import ObservationsGenerator
from hps.rl.settings import ObservationSettings, SacSettings, AgentAlgorithm
from hps.rl.environment.hscomponents import HSystem

from stable_baselines3 import SAC, A2C, TD3, PPO, DDPG
from stable_baselines3.common.noise import OrnsteinUhlenbeckActionNoise


def linear_schedule(initial_value: float) -> Callable[[float], float]:
    def func(progress_remaining: float) -> float:
        return 0.1 * (9 * progress_remaining + 1) * initial_value

    return func


class AgentBuilder:
    def __init__(
        self,
        algoritm: AgentAlgorithm,
        sac_params: SacSettings,
        train_env: HSEnvironment,
        observations_generator: ObservationsGenerator,
        initial_steps_to_collect: int,
    ):
        self.sac_params = sac_params
        self.algoritm = algoritm
        self.train_env = train_env
        self.observations_generator = observations_generator
        self.initial_steps_to_collect = initial_steps_to_collect

    def build(self, num_actions, output_checkpoint_folder, input_checkpoint_folder):

        if input_checkpoint_folder is not None:
            agent = SAC.load(os.path.join(input_checkpoint_folder, "best_model"))
            agent.set_env(self.train_env)
            agent.tau = self.sac_params.target_update_tau
            agent.learning_rate = self.sac_params.actor.learning_rate
            return agent

        mu = np.zeros(num_actions)
        # sigma = np.ones(num_actions) * 0.3
        # action_noise = OrnsteinUhlenbeckActionNoise(mu, sigma, theta=0.5)
        sigma = np.ones(num_actions) * 0.4
        action_noise = OrnsteinUhlenbeckActionNoise(mu, sigma)

        gradient_steps = 1  # train_intervals // 256 + 1
        tb_log_folder = output_checkpoint_folder + "/tb_logs"

        policy = "MultiInputPolicy"

        if self.observations_generator.observation_settings.time_periods:
            observation_space = self.observations_generator.get_space(
                step=0,
                hydro_system=self.train_env.hydro_system,
                current_price=self.train_env.current_price,
                current_inflow=self.train_env.current_inflow,
            )
            features_extractor_class = TimeFourierFeatureExtractor
            features_extractor_kwargs = dict(time_periods=self.observations_generator.observation_settings.time_periods)
        else:
            observations = self.observations_generator.get_observations(
                step=0,
                hydro_system=self.train_env.hydro_system,
                current_price=self.train_env.current_price,
                current_inflow=self.train_env.current_inflow,
            )
            feature_dim = len(observations)
            features_extractor_class = CombinedIdentityExtractor
            features_extractor_kwargs = dict()

        if self.algoritm == AgentAlgorithm.SAC:
            policy_kwargs = dict(
                net_arch=dict(pi=self.sac_params.actor.structure, qf=self.sac_params.critic.structure),
                features_extractor_class=features_extractor_class,
                features_extractor_kwargs=features_extractor_kwargs,
            )
            agent = SAC(
                policy,
                self.train_env,
                verbose=1,
                policy_kwargs=policy_kwargs,
                gradient_steps=gradient_steps,
                learning_rate=self.sac_params.actor.learning_rate,
                learning_starts=self.initial_steps_to_collect,
                gamma=1.0,
                tau=self.sac_params.target_update_tau,
                use_sde=True,
                target_update_interval=self.sac_params.target_update_period,
                action_noise=action_noise,
                tensorboard_log=tb_log_folder,
            )
        elif self.algoritm == AgentAlgorithm.A2C:
            agent = A2C(policy, self.train_env, verbose=1, tensorboard_log=tb_log_folder)
        elif self.algoritm == AgentAlgorithm.TD3:
            agent = TD3(
                policy, self.train_env, verbose=1, gamma=1.0, action_noise=action_noise, tensorboard_log=tb_log_folder
            )
        elif self.algoritm == AgentAlgorithm.PPO:
            agent = PPO(policy, self.train_env, verbose=1, tensorboard_log=tb_log_folder)
        elif self.algoritm == AgentAlgorithm.DDPG:
            agent = DDPG(
                policy, self.train_env, verbose=1, gamma=1.0, action_noise=action_noise, tensorboard_log=tb_log_folder
            )

        if input_checkpoint_folder is not None:
            agent = agent.load(os.path.join(input_checkpoint_folder, "best_model"))

        return agent
