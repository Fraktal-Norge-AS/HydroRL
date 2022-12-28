from hydro_system_models import hydro_system_large, hydro_system_medium, hydro_system_small


class SystemManager:
    def __init__(self):
        self.system_lookup = {
            "large": hydro_system_large(),
            "medium": hydro_system_medium(),
            "small": hydro_system_small()
        }

    def get_system(self, system_name):
        if not system_name in self.system_lookup:
            raise ValueError("Unknown system : {0}".format(system_name))

        return self.system_lookup[system_name]
