from hps.rl.logging.agent_plugin import AgentPlugin
from hps.rl.settings import RunSettings
import tensorflow as tf
from tensorboard.plugins.hparams import api as hp
from matplotlib import pyplot as plt
import io
from hps.rl.logging.view_networks import histogram_trainable_actor_variables, histogram_trainable_critic_variables

# Plotting
LW = 3
FIGSIZE = (16, 9)


class TensorboardLogger(AgentPlugin):
    def __init__(self, log_dir, run_settings: RunSettings, eval_image_interval=10):
        self.train_summary_writer = tf.summary.create_file_writer(log_dir)
        self.eval_image_interval = eval_image_interval
        self.call_counter = 0
        self.run_settings = run_settings

    def should_terminate(self):
        return False

    def get_h_params_from_object(self, obj):
        result = []
        for k, v in obj.__dict__.items():
            if isinstance(v, int) or isinstance(v, float):
                result.append((hp.HParam(k, hp.Discrete([v])), v))
        return result

    def log_h_params(self, run_settings):
        items = self.get_h_params_from_object(run_settings) + self.get_h_params_from_object(run_settings.sac_settings)
        h_params = {k: v for (k, v) in items}

        with self.train_summary_writer.as_default():
            hp.hparams(h_params)

    def log_initial_values(self, eval_env):
        self.plot_price(1, eval_env)
        self.plot_inflows(1, eval_env)

    def log_eval_episode(self, step, episode_name, eval_env):
        pass

    def log_info(
        self,
        step,
        eval_env,
        returns,
        avg_return,
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

        with self.train_summary_writer.as_default():
            for col in eval_env.reward.columns:
                tf.summary.scalar("return/" + col, eval_env.reward[col].sum(), step=step)
            tf.summary.scalar("return/new_best_train", new_best["train"], step=step)
            tf.summary.scalar("return/new_best_eval", new_best["eval"], step=step)

            for col in eval_env.report_df.columns:
                tf.summary.scalar("report/sum_" + col, eval_env.report_df[col].sum(), step=step)

            tf.summary.scalar("loss/total_loss", train_loss.loss, step=step)
            tf.summary.scalar("loss/critic_loss", train_loss[1].critic_loss, step=step)
            tf.summary.scalar("loss/actor_loss", train_loss[1].actor_loss, step=step)
            tf.summary.scalar("return/avg_return", avg_return, step=step)
            tf.summary.scalar("return/train_avg_return", train_metrics[0].result().numpy(), step=step)
            tf.summary.scalar("steps/train_avg_steps", train_metrics[1].result().numpy(), step=step)

            observation_gradients = eval_env.gradient_df

            if new_best["eval"]:
                tf.summary.scalar("return/best_train", current_best["train"], step=step)
                tf.summary.scalar("return/best_eval", current_best["eval"], step=step)
                self.plot_prod_and_volume("best/", step, eval_env)
                self.plot_rewards("best/rewards", rewards, step)
                self.plot_report(step, eval_env, "best/report")
                # self.plot_q_value(step, q_value_tuple, "best/q_value")
                self.plot_gradients("best/gradients", step, observation_gradients)

            if self.call_counter >= self.eval_image_interval:
                self.plot_prod_and_volume("eval/", step, eval_env)
                self.plot_rewards("eval/rewards", rewards, step)
                self.plot_report(step, eval_env, "eval/report")
                # self.plot_q_value(step, q_value_tuple, "eval/q_value")
                self.plot_gradients("eval/gradients", step, observation_gradients)
                self.call_counter = 0

        self.train_summary_writer.flush()  # Force flush
        self.call_counter += 1

    def plot_q_value(self, step, q_value_tuple, plot_name):
        if q_value_tuple is None:
            return
        q_val, volume, steps = q_value_tuple
        fig, axis = plt.subplots(1, figsize=FIGSIZE)
        axis.plot(steps, q_val, label=volume)
        tf.summary.image(plot_name, self.plot_to_image(fig), step, 1)

    def plot_to_image(self, figure):
        """
        Converts the matplotlib plot specified by 'figure' to a PNG image and
        returns it. The supplied figure is closed and inaccessible after this call.
        """
        # Save the plot to a PNG in memory.
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        # Closing the figure prevents it from being displayed directly inside
        # the notebook.
        plt.close(figure)
        buf.seek(0)
        # Convert PNG buffer to TF image
        image = tf.image.decode_png(buf.getvalue(), channels=4)
        # Add the batch dimension
        image = tf.expand_dims(image, 0)
        return image

    def plot_gradients(self, plot_name, step, gradients):
        fig, axis = plt.subplots(1, figsize=FIGSIZE)
        for obs in gradients.columns:
            axis.plot(gradients[obs], lw=LW, label=obs)
        axis.legend()
        tf.summary.image(plot_name + "gradients", self.plot_to_image(fig), step, 1)

    def plot_prod_and_volume(self, plot_name, step, eval_env):
        fig, axis = plt.subplots(1, figsize=FIGSIZE)

        for res in eval_env.hydro_system.reservoirs:
            if not res.is_ocean:
                axis.plot(eval_env.report_df[res.name], lw=LW, label=res.name)
        axis.legend()
        tf.summary.image(plot_name + "vol", self.plot_to_image(fig), step, 1)

        fig, axis = plt.subplots(1, figsize=FIGSIZE)
        for ps in eval_env.hydro_system.stations:
            axis.plot(eval_env.report_df["Power_" + ps.name], lw=LW, label=ps)
        axis.legend()
        tf.summary.image(plot_name + "prod", self.plot_to_image(fig), step, 1)

    def plot_volume_and_spill(self, step, eval_env, plot_name):
        fig, axis = plt.subplots(1, figsize=FIGSIZE)
        axis2 = axis.twinx()

        axis.set_ylabel("Volume [Mm3]")
        for res in eval_env.hydro_system.reservoirs:
            if not res.is_ocean:
                axis.plot(eval_env.report_df[res.name], lw=LW, label=res.name)
                axis2.plot(
                    eval_env.report_df["Spill_" + res.spillage.get_name()],
                    lw=LW,
                    label=res.spillage.get_name(),
                    color="g",
                )
        axis.legend()
        axis2.legend()

        color = "g"
        axis2.set_ylabel("Spillage [Mm3]", color=color)
        axis2.tick_params(axis="y", labelcolor=color)

        fig.tight_layout()
        tf.summary.image(plot_name + "vol_spi", self.plot_to_image(fig), step, 1)

    def plot_rewards(self, plot_name, rewards, step):
        fig, axis = plt.subplots(1, figsize=FIGSIZE)
        for i in range(len(rewards)):
            axis.plot(rewards[i])
        tf.summary.image(plot_name, self.plot_to_image(fig), step, 1)

    def plot_price(self, step, eval_env, plot_name="price"):
        fig, axis = plt.subplots(1, figsize=(20, 10))
        axis.plot(eval_env.current_price)
        tf.summary.image("exogeneous/" + plot_name, self.plot_to_image(fig), step, 1)

    def plot_report(self, step, eval_env, plot_name="report"):
        for col in eval_env.report_df.columns:
            fig, axis = plt.subplots(1, figsize=FIGSIZE)
            axis.plot(eval_env.report_df[col])
            axis.title.set_text(col)

            tf.summary.image("report/" + col, self.plot_to_image(fig), step, 1)

    def plot_inflows(self, step, eval_env, plot_name="inflows"):
        n_inflows = len(eval_env.current_inflow)
        fig, axis = plt.subplots(1, figsize=(20, 10))

        for res in eval_env.current_inflow:
            reservoir_inflow = eval_env.current_inflow[res]
            axis.plot(reservoir_inflow, lw=LW)
            axis.title.set_text(res)

        tf.summary.image("exogeneous/" + plot_name, self.plot_to_image(fig), step, 1)


class TensorBoardTuningLogger(TensorboardLogger):
    def __init__(self, log_dir, run_settings: RunSettings, h_params, eval_image_interval=10):
        super(TensorBoardTuningLogger, self).__init__(log_dir, run_settings, eval_image_interval=10)
        self.h_params = h_params

    def log_h_params(self, run_settings=None):
        if self.h_params:
            with self.train_summary_writer.as_default():
                hp.hparams(self.h_params)

    def log_info(
        self,
        step,
        eval_env,
        returns,
        avg_return,
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

        with self.train_summary_writer.as_default():

            tf.summary.scalar("loss/total_loss", train_loss.loss, step=step)
            tf.summary.scalar("loss/critic_loss", train_loss[1].critic_loss, step=step)
            tf.summary.scalar("loss/actor_loss", train_loss[1].actor_loss, step=step)
            tf.summary.scalar("return/avg_return", avg_return, step=step)
            tf.summary.scalar("return/train_avg_return", train_metrics[0].result().numpy(), step=step)
            tf.summary.scalar("alpha", alpha, step=step)

            histogram_trainable_critic_variables(weights.c1_weights, step, "Target Critic1")
            histogram_trainable_critic_variables(weights.c2_weights, step, "Target Critic2")
            histogram_trainable_actor_variables(weights.a_encoding_weights, weights.a_projection_weights, step)

            observation_gradients = eval_env.gradient_df

            if new_best["eval"]:
                tf.summary.scalar("return/best_train", current_best["train"], step=step)
                tf.summary.scalar("return/best_eval", current_best["eval"], step=step)
                self.plot_prod_and_price(step, eval_env, "best/")
                self.plot_volume_and_price(step, eval_env, "best/")
                self.plot_volume_and_spill(step, eval_env, "best/")
                self.plot_gradients("best/gradients", step, observation_gradients)

            if self.call_counter >= self.eval_image_interval:
                self.plot_prod_and_price(step, eval_env, "eval/")
                self.plot_volume_and_price(step, eval_env, "eval/")
                self.plot_volume_and_spill(step, eval_env, "eval/")
                self.plot_gradients("eval/gradients", step, observation_gradients)
                self.call_counter = 0

        self.train_summary_writer.flush()  # Force flush
        self.call_counter += 1

    def plot_prod_and_price(self, step, eval_env, plot_name):
        fig, axis = plt.subplots(1, figsize=FIGSIZE)

        axis.set_ylabel("MW")
        for ps in eval_env.hydro_system.stations:
            axis.plot(eval_env.report_df["Power_" + ps.name], lw=LW, label=ps.name)
        axis.legend()

        axis2 = axis.twinx()
        color = "r"
        axis2.set_ylabel("[EUR/MWH]", color=color)
        axis2.tick_params(axis="y", labelcolor=color)
        axis2.plot(eval_env.current_price, color=color)

        fig.tight_layout()
        tf.summary.image(plot_name + "prod_n_price", self.plot_to_image(fig), step, 1)

    def plot_volume_and_price(self, step, eval_env, plot_name):
        fig, axis = plt.subplots(1, figsize=FIGSIZE)

        axis.set_ylabel("RES")
        for res in eval_env.hydro_system.reservoirs:
            if not res.is_ocean:
                axis.plot(eval_env.report_df[res.name], lw=LW, label=res.name)
        axis.legend()

        axis2 = axis.twinx()
        color = "r"
        axis2.set_ylabel("[EUR/MWH]", color=color)
        axis2.tick_params(axis="y", labelcolor=color)
        axis2.plot(eval_env.current_price, color=color)

        fig.tight_layout()
        tf.summary.image(plot_name + "volume_n_price", self.plot_to_image(fig), step, 1)


class TensorboardTrainLogger:
    """Used for more frequent logging from training."""

    def __init__(self, log_dir, run_settings: RunSettings, moving_average_window=20):
        self.train_summary_writer = tf.summary.create_file_writer(log_dir)

        # self.reward_deque = tf_metrics.TFDeque(
        #     max_len=moving_average_window, dtype=tf.float32, name=f"MovingAverage{moving_average_window}")
        # self.eval_deque = tf_metrics.TFDeque(
        #     max_len=run_settings.agent_settings[0].eval_episodes, dtype=tf.float32, name="EvalAverage")

    def log_info(self, step, train_loss, weights):
        with self.train_summary_writer.as_default():

            tf.summary.scalar("loss/total_loss", train_loss.loss, step=step)
            tf.summary.scalar("loss/critic_loss", train_loss[1].critic_loss, step=step)
            tf.summary.scalar("loss/actor_loss", train_loss[1].actor_loss, step=step)
            tf.summary.scalar("loss/alpha_loss", train_loss[1].alpha_loss, step=step)

            histogram_trainable_critic_variables(weights.c1_weights, step, "Critic1")
            histogram_trainable_critic_variables(weights.c2_weights, step, "Critic2")
            histogram_trainable_critic_variables(weights.c1_target_weights, step, "Target Critic1")
            histogram_trainable_critic_variables(weights.c2_target_weights, step, "Target Critic2")
            histogram_trainable_actor_variables(weights.a_encoding_weights, weights.a_projection_weights, step)

    def log_episode(self, train_metrics, step):
        self.reward_deque.add(train_metrics[0].result())
        self.eval_deque.add(train_metrics[0].result())
        with self.train_summary_writer.as_default():
            for m in train_metrics:
                tf.summary.scalar(f"metric/{m.name}", m.result(), step=step)
                tf.summary.scalar(f"metric/acc_mean_reward", self.reward_deque.mean(), step=step)

    def log_evaluation(self, train_metrics, step):
        with self.train_summary_writer.as_default():
            tf.summary.scalar(f"metric/eval_mean_reward", self.eval_deque.mean(), step=step)
        self.eval_deque.clear()
