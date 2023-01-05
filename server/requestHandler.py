#%%
import io
import numpy as np
import jsonpickle.ext.pandas as pickle_pandas
import jsonpickle.ext.numpy as pickle_numpy
from hps.utils.draw_hydro_system import draw_hydro_system
from system_manager import SystemManager
from matplotlib.backends.backend_agg import FigureCanvasAgg
from evaluator import start_evalaution
from project_runner import start_run_project
from project_status import ProjectStatus
from hps.rl.settings import RunSettings, RunSettingsSerializer
from server.namegenerator import get_random_names
from server.appsettings import appSettings
from hps.utils.serializer import HydroSystemSerializer


class RequestHandler:
    def __init__(self):
        self.system_manager = SystemManager()
        pickle_pandas.register_handlers()
        pickle_numpy.register_handlers()

    def start_agents(self, project_uid, run_id):
        status = ProjectStatus(project_uid)

        if not status.is_running(run_id):
            print("Starting agents for " + project_uid + ", " + str(run_id))
            start_run_project(project_uid, run_id)
            return "started"
        else:
            print("Already running")
        return "already_started"

    def evaluate(self, eval_id):
        start_evalaution(eval_id)
        return "evalauting"

    def get_image(self, system):
        hs = self.system_manager.get_system(system)
        drawing = draw_hydro_system(hs, system)
        drawing.patch.set_alpha(0)
        output = io.BytesIO()
        FigureCanvasAgg(drawing).print_png(output)
        return output

    def create_run_settings(self, project_uid, agent_id):
        settings = RunSettings()
        settings.uid = project_uid  # NB: Shouldnt this be project_run_uid?
        settings.train_episodes = 1000000
        status = ProjectStatus(project_uid)

        if agent_id is not None:
            settings.agent_settings = settings.agent_settings[:1]
            settings.start_checkpoint_folder = status.get_start_folder(agent_id)
        else:
            agent_count = len(settings.agent_settings)

            seeds = (100 + np.random.choice(500, size=agent_count, replace=False)).astype(int)
            names = get_random_names(agent_count * 10)

            for i, agent in enumerate(settings.agent_settings):
                agent.seed = seeds[i]
                agent.name = names[i]
                agent.output_checkpoint_folder = appSettings.get_checkpoint_folder(settings.uid, agent.name)

                settings.spare_agent_names = names[agent_count:]
        settings.system = status.hydro_system.Name

        settings.start_volumes = status.get_start_volumes()

        return RunSettingsSerializer.serialize(settings)

    def get_system(self, system):
        hs = self.system_manager.get_system(system)
        return HydroSystemSerializer.serialize(hs)
