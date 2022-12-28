import json
from server.settings_file import SETTINGS_FILE

# Figure out how to set this
class AppSettings:
    def __init__(self):
        self.settings = json.load(open(SETTINGS_FILE))

    def use_gpu(self):
        return True

    def get_connection_string(self):
        return self.settings["ConnectionStrings"]["PConnection"]

    def get_connection_string_log(self):
        return self.settings["ConnectionStrings"]["PLogConnection"]

    def get_workspace_folder(self):
        return self.settings["WorkspaceDir"]

    def get_checkpoint_folder(self, project_run_uid, agent_name):
        return self.get_workspace_folder() + "projects/" + project_run_uid + "/" + agent_name + "/checkpoints"

    def get_logging_config(self):
        return self.settings["PLogConfig"]


appSettings = AppSettings()
