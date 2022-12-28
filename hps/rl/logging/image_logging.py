import matplotlib.pyplot as plt
from stable_baselines3.common.logger import Figure

# Plotting
LW = 3
FIGSIZE = (16, 9)


class ImageLogging:
    @staticmethod
    def plot_prod_and_price(logger, eval_env, plot_name="ProdAndPrice"):
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
        logger.record("images/" + plot_name, Figure(fig, close=True), exclude=("stdout", "log", "json", "csv"))
        plt.close()
