import numpy as np
from hps.rl.settings import RunSettings, AgentSettings
from hps.rl.logging.agent_plugin import AgentPlugin
from hps.rl.sb_callback import EvalCallback

import os

from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3 import SAC


class AgentRunner:
    def __init__(
        self,
        run_settings: RunSettings,
        agent_settings: AgentSettings,
        sb_agent,
        internal_train_env,
        internal_eval_env,
        plugin: AgentPlugin,
    ):

        self.sb_agent = sb_agent
        self.plugin = plugin
        self.internal_train_env, self.internal_eval_env = internal_train_env, internal_eval_env

        self.eval_env = self.internal_eval_env

        self.init_agent(agent_settings, run_settings.train_intervals)

        self.log_replay_buffer_when_finished = run_settings.log_replay_buffer_when_finished
        self.eval_interval = agent_settings.eval_interval
        self.eval_episodes = agent_settings.eval_episodes
        self.train_episodes = run_settings.train_episodes
        self.train_intervals = run_settings.train_intervals
        self.trains_per_episode = run_settings.trains_per_episode
        self.steps_per_episode = run_settings.train_intervals
        self.episodes_to_initially_collect = agent_settings.episodes_to_initially_collect
        self.plugin.log_h_params(run_settings)

    def init_agent(self, agent_settings: AgentSettings, train_intervals: int):

        eval_freq = agent_settings.eval_interval * train_intervals
        self.best_model_path = agent_settings.output_checkpoint_folder
        self.eval_callback = EvalCallback(
            self,
            self.eval_env,
            best_model_save_path=agent_settings.output_checkpoint_folder,
            log_path=agent_settings.output_checkpoint_folder + "/tb_logs/eval",
            eval_freq=eval_freq,
            deterministic=True,
            render=False,
            n_eval_episodes=agent_settings.eval_episodes,
        )

    def evaluate_callback(self, step, mean_reward, best_mean_reward, new_best_eval, episode_rewards):
        new_best = {"eval": new_best_eval, "train": False}

        current_best = {"eval": best_mean_reward, "train": -0.0}

        eval_env = self.internal_eval_env
        self.plugin.log_info(
            int(step),
            eval_env,
            episode_rewards,
            mean_reward,
            current_best,
            new_best,
            episode_rewards,
            episode_rewards,
            0,
            None,
            0,
            0,
            0,
            0,
        )

    def __evaluate(self, step):
        rewards = []
        for i in range(self.eval_episodes):
            self.internal_eval_env.inflow_price_sampler.raw_index = i
            _, _ = evaluate_policy(
                self.sb_agent.policy,
                self.eval_env,
                n_eval_episodes=1,
                render=False,
                deterministic=True,
                return_episode_rewards=True,
                warn=False,
            )

            self.plugin.log_eval_episode(
                step=step, episode_name=self.internal_eval_env.forecast_name, eval_env=self.internal_eval_env
            )

            rewards.append(self.internal_eval_env.reward["sum"].sum())
        avg_return = np.mean(rewards)

        return avg_return

    def evaluate(self, step, current_best, train_loss, is_eval=True):
        avg_return = self.__evaluate(step)
        if avg_return > current_best["eval"]:
            current_best["eval"] = avg_return
        return current_best

    def end_report(self):
        self.sb_agent = SAC.load(os.path.join(self.best_model_path, "best_model"))
        best_step = self.plugin.get_best_step()
        self.__evaluate(best_step)
        if self.log_replay_buffer_when_finished:
            self.sb_agent.save_replay_buffer(self.best_model_path + "/replay_buffer")

    def run(self):
        num_steps = self.train_episodes * self.steps_per_episode
        self.sb_agent.learn(total_timesteps=num_steps, callback=self.eval_callback)
        self.end_report()
        del self.sb_agent
