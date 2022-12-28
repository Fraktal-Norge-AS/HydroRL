"""
Top-level package for hps.
"""

__author__ = "Fraktal Norge AS"
__copyright__ = ""
__credits__ = [""]
__version__ = "0.1.0"


from hps.system.edges import Discharge, Bypass, Spillage  # noqa
from hps.system.nodes import Reservoir, PowerStation, Creek, Gate, Ocean  # noqa
from hps.system.inflow import ScaleInflowModel, ScaleYearlyInflowModel, SimpleInflowModel  # noqa

from .hydro_system import HydroSystem  # noqa

from hps.system.head_function import ConstantHeadFunction, HeadFunction  # noqa
from hps.system.generation_function import GenerationHeadFunction, ConstantGenerationFunction


from hps.utils import LinearFunctionApprox, SplineFunctionApprox, CubicSpline, get_continuous_color  # noqa

from hps.utils.serializer import HSJSONEncoder, HydroSystemSerializer  # noqa

from hps.utils.draw_hydro_system import draw_hydro_system  # noqa
