#%%
from hps.rl.environment.hsenvironment import *
import json
from hps.system.head_function import HeadFunction
from hps.generation_function.generation_head_function import GenerationHeadFunction


class CustomEncoder(json.JSONEncoder):
    def default(self, o):

        key = "__{}__".format(o.__class__.__name__)
        dictionary = o.__dict__
        if isinstance(o, VariableInflowAction):
            dictionary["res"] = o.res.name
        elif isinstance(o, StationAction):
            dictionary["upper_res"] = o.upper_res.name
            dictionary["station"] = o.station.name
            dictionary["lower_res"] = o.lower_res.name
        # elif isinstance(o, PickGateAction):
        #     vals = [c.name for c in o.input_actions]
        #     dictionary["input_actions"] = vals

        return {key: dictionary}


class HSSerialaizer:
    def serialize(system):
        return json.dumps(system, cls=CustomEncoder)

    def hook(o):
        obj = None
        if "__HSystem__" in o:
            obj = HSystem(None, None, None, None, None)
            obj.__dict__.update(o["__HSystem__"])
        elif "__HeadFunction__" in o:
            obj = HeadFunction(1, 2)
            obj.__dict__.update(o["__HeadFunction__"])
        elif "__Res__" in o:
            obj = Res(None, None, None, None, None)
            obj.__dict__.update(o["__Res__"])
        elif "__Station__" in o:
            obj = Station(None, None, None, None, None, None)
            obj.__dict__.update(o["__Station__"])
        elif "__GenerationHeadFunction__" in o:
            obj = GenerationHeadFunction(1, 2, 1, 2, None)
            obj.__dict__.update(o["__GenerationHeadFunction__"])
        elif "__VariableInflowAction__" in o:
            obj = VariableInflowAction(None, None, None)
            obj.__dict__.update(o["__VariableInflowAction__"])
        elif "__StationAction__" in o:
            obj = StationAction(None, None, None, None)
            obj.__dict__.update(o["__StationAction__"])
        elif "__PickGateAction__" in o:
            obj = PickGateAction(None, None)
            obj.__dict__.update(o["__PickGateAction__"])
        else:
            print("Missing", o)

        if obj is not None:
            return obj
        return o

    def fix_action_refs(action, res_lookup, stat_lookup, action_lookup):
        if isinstance(action, VariableInflowAction):
            action.res = res_lookup[action.res]
        elif isinstance(action, StationAction):
            action.upper_res = res_lookup[action.upper_res]
            action.station = stat_lookup[action.station]
            action.lower_res = res_lookup[action.lower_res]
        elif isinstance(action, PickGateAction):
            HSSerialaizer.fix_action_refs(action.input_actions, res_lookup, stat_lookup, action_lookup)

    def deserialze(json_text):
        deserialized = json.loads(json_text, object_hook=HSSerialaizer.hook)

        res_lookup = {res.name: res for res in deserialized.reservoirs}
        stat_lookup = {stat.name: stat for stat in deserialized.stations}
        action_lookup = {a.name: a for a in deserialized.sorted_actions}

        for action in deserialized.sorted_actions:
            HSSerialaizer.fix_action_refs(action, res_lookup, stat_lookup, action_lookup)

        return deserialized
