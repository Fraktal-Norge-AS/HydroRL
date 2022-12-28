#%%

import json
import numpy as np

from hps.system.nodes import Creek, Reservoir, PowerStation, Ocean, Gate
from hps.system.edges import Bypass, Spillage, Discharge
from hps import HydroSystem

from hps.utils.function_approx import LinearFunctionApprox, SplineFunctionApprox
from hps.system.generation_function import ConstantGenerationFunction
from hps.system.generation_function.generation_head_function import (
    GenerationHeadFunction,
    VanillaGenerationHeadFunction,
)
from hps.system.head_function import ConstantHeadFunction, LinearHeadFunction, ExpHeadFunction, HeadFunction
from hps.system.inflow import NullInflow, ScaleInflowModel, ScaleYearlyInflowModel, SimpleInflowModel


class HSJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return {"array": obj.tolist()}
        elif isinstance(obj, complex):
            return [obj.real, obj.imag]
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, bytes):
            return obj.decode()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, bool):
            return int(obj)
        else:
            key = "{}".format(obj.__class__.__name__)
            dictionary = obj.__dict__
            return {key: dictionary}


class HydroSystemSerializer:
    cls = set(
        [
            "LinearFunctionApprox",
            "SplineFunctionApprox",
            "ConstantGenerationFunction",
            "GenerationHeadFunction",
            "VanillaGenerationHeadFunction",
            "ConstantHeadFunction",
            "LinearHeadFunction",
            "ExpHeadFunction",
            "HeadFunction",
            "NullInflow",
            "ScaleInflowModel",
            "ScaleYearlyInflowModel",
            "SimpleInflowModel",
            "Discharge",
            "Bypass",
            "Spillage",
            "Ocean",
            "Gate",
            "Creek",
            "Reservoir",
            "PowerStation",
        ]
    )

    @staticmethod
    def serialize(hydro_system: HydroSystem):
        return json.dumps(hydro_system.to_dict(), cls=HSJSONEncoder, ensure_ascii=False)

    @staticmethod
    def deserialize(json_text):
        return json.loads(json_text, object_hook=HydroSystemSerializer.hook)

    @staticmethod
    def hook(o):
        obj = None
        intersect = HydroSystemSerializer.cls.intersection(set(o.keys()))
        if intersect:
            cls_name = list(intersect)[0]
            kwargs = o[cls_name]
            obj = globals()[cls_name](**kwargs)
        elif "array" in o:
            obj = np.array(o["array"])
        elif "HydroSystem" in o:
            obj = HydroSystem(
                name=o["HydroSystem"]["name"],
                nodes=(
                    o["HydroSystem"]["reservoirs"]
                    + o["HydroSystem"]["power stations"]
                    + o["HydroSystem"]["oceans"]
                    + o["HydroSystem"]["creeks"]
                    + o["HydroSystem"]["gates"]
                ),
            )

            edges = o["HydroSystem"]["discharges"] + o["HydroSystem"]["spillages"] + o["HydroSystem"]["bypasses"]
            for edge in edges:
                parent_node = [node for node in obj.nodes if node.name == edge.parent][0]  # Assume unique names
                child_node = [node for node in obj.nodes if node.name == edge.child][0]  # Assume unique names
                edge.parent = parent_node
                edge.child = child_node

            obj.add_edges_from(edges)

        if obj is not None:
            return obj
        return o


# %%
def dummy():
    # %%

    from hps.utils.draw_hydro_system import draw_hydro_system, view_graph
    from hydro_system_models import hydro_system_small, hydro_system_large, hydro_system_medium
    
    hydro_systems = [hydro_system_small(), hydro_system_medium(), hydro_system_large()]
    hs = hydro_systems[-1]

    hs_json = HydroSystemSerializer.serialize(hs)
    hs_ = HydroSystemSerializer.deserialize(hs_json)

    hs__json = HydroSystemSerializer.serialize(hs_)
    hs__ = HydroSystemSerializer.deserialize(hs__json)

    assert json.dumps(hs__.to_dict(), cls=HSJSONEncoder) == json.dumps(hs_.to_dict(), cls=HSJSONEncoder)

    print(json.dumps(hs__.to_dict(), cls=HSJSONEncoder, indent=4))  # .encode('latin-1'))
    print(json.dumps(hs.to_dict(), cls=HSJSONEncoder, ensure_ascii=False))  # .encode('iso-8859-1')

    draw_hydro_system(hs)
    draw_hydro_system(hs_)
    view_graph(hs_)
    view_graph(hs)


# %%
