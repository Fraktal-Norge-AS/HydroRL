
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from hps.system.nodes.reservoir import Reservoir
from hps import draw_hydro_system
from hps.rl.builders.hydro_rl_builder import HydroRLBuilder
import hydro_system_models as hsm
from hydro_system_models import hydro_system_medium, hydro_system_small, hydro_system_large
from hps.hydro_system import HydroSystemPostCalculations
from hps.utils.serializer import HydroSystemSerializer

hydro_system = hydro_system_medium()

hs_serr = HydroSystemSerializer.serialize(hydro_system)
hydro_system = HydroSystemSerializer.deserialize(hs_serr)

# HydroSystemPostCalculations.compute_reservoir_energy_equivalents(hydro_system)
system = HydroRLBuilder.Build(hydro_system)
draw_hydro_system(hydro_system)

system.report()
print("")

print("name, min_vol, max_vol, en_eq")
for node in hydro_system.reservoirs:
    print(node.name, node.min_volume, node.max_volume, node.energy_equivalent)

print("name, p_min, p_max, en_eq")
for node in hydro_system.power_stations:
    print(node.name, node.generation_function.p_min, node.generation_function.p_max, node.energy_equivalent)
