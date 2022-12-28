from abc import abstractmethod
from tensorboard.plugins.hparams import api as hp


class AgentPlugin(object):
    @abstractmethod
    def should_terminate(self):
        pass

    @abstractmethod
    def log_eval_episode(self, step, episode_name, eval_env):
        pass

    @abstractmethod
    def log_info(
        self,
        step,
        eval_env,
        returns,
        sum_return,
        current_best,
        new_best,
        rewards,
        end_rewards,
        train_metrics,
        train_loss,
        q_value_tuple,
        q_value,
        alpha,
    ):
        pass

    @abstractmethod
    def log_initial_values(self, eval_env):
        pass

    @abstractmethod
    def log_h_params(self, run_settings):
        pass

    def get_h_params_from_object(self, obj):
        result = []
        for k, v in obj.__dict__.items():
            if isinstance(v, int) or isinstance(v, float):
                result.append((hp.HParam(k, hp.Discrete([v])), v))
        return result


class CompositePlugin(AgentPlugin):
    def __init__(self, plugins):
        self.plugins = plugins

    def should_terminate(self):
        return any([p.should_terminate() for p in self.plugins])

    def log_info(
        self,
        step,
        eval_env,
        returns,
        sum_return,
        current_best,
        new_best,
        rewards,
        end_rewards,
        train_metrics,
        train_loss,
        q_value_tuple,
        q_value,
        alpha,
        weights,
    ):
        [
            p.log_info(
                step,
                eval_env,
                returns,
                sum_return,
                current_best,
                new_best,
                rewards,
                end_rewards,
                train_metrics,
                train_loss,
                q_value_tuple,
                q_value,
                alpha,
                weights,
            )
            for p in self.plugins
        ]

    def log_initial_values(self, eval_env):
        [p.log_initial_values(eval_env) for p in self.plugins]

    def log_eval_episode(self, step, episode_name, eval_env):
        [p.log_eval_episode(step, episode_name, eval_env) for p in self.plugins]

    def log_h_params(self, run_settings):
        [p.log_h_params(run_settings) for p in self.plugins]

    def get_best_step(self):
        return self.plugins[0].get_best_step


class ConsoleLogger(AgentPlugin):
    def __init__(self):
        self.current_best_step = 0

    def should_terminate(self):
        return False

    def log_info(
        self,
        step,
        eval_env,
        returns,
        sum_return,
        current_best,
        new_best,
        rewards,
        end_rewards,
        train_metrics,
        train_loss,
        q_value_tuple,
        q_value,
        alpha,
        weights,
    ):

        if new_best:
            self.current_best_step = step

        current_best_str = ""
        for i in current_best:
            current_best_str += "{}: {:.2f} ".format(i, current_best[i])

        end_rewards_str = "[ "
        for i in end_rewards:
            end_rewards_str += "{:.3f} ".format(i)
        end_rewards_str += "]"

        print("{:<7} | {:>10.4f} | {} | {} ".format(step, sum_return, current_best_str, end_rewards_str))

    def get_best_step(self):
        return self.current_best_step

    def log_eval_episode(self, step, episode_name, eval_env):
        pass

    def log_initial_values(self, eval_env):
        print("{:=^60}".format(" Console logger "))
        print("Step    | Sum return |     Current best returns    | End rewards ")

    def log_h_params(self, run_settings):
        items = self.get_h_params_from_object(run_settings) + self.get_h_params_from_object(run_settings.sac_settings)
        h_params = {k: v for (k, v) in items}

        print("{:=^60}".format(" Hyperparameters "))
        for h in h_params:
            print("{:<38}: {:>20}".format(h.name, h_params[h]))
