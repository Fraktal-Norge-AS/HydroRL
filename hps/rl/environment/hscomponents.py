from typing import List, Optional
from abc import abstractmethod
from networkx.algorithms.centrality.load import newman_betweenness_centrality
import numpy as np
from numpy.testing._private.utils import print_assert_equal

from hps.rl.logging.report_name import ReportName
from hps.system.head_function import IHeadFunction


class HSComponent(object):
    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_value(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def report(self):
        pass

    @abstractmethod
    def report_state(self, state):
        pass


class Res(HSComponent):
    def __init__(
        self,
        name,
        min_volume,
        max_volume,
        init_volume,
        end_volume,
        spillage,
        inflow_model=None,
        is_ocean=False,
        head: Optional[IHeadFunction] = None,
        energy_equivalent=None,
    ):
        self.name = name
        self.min_volume = min_volume  # [Mm3]
        self.max_volume = max_volume  # [Mm3]
        self.end_volume = end_volume  # [Mm3]
        self.init_volume = init_volume  # [Mm3]
        self.current_volume = init_volume  # [Mm3]
        self.is_ocean = is_ocean
        self.spillage = spillage
        self.inflow_model = inflow_model
        self.head = head
        self.energy_equivalent = energy_equivalent  # [kWh/m3]

    def reset(self):
        self.current_volume = self.init_volume

    def get_name(self):
        return self.name

    def get_value(self):
        return self.current_volume

    def get_head(self, delta_volume):
        """Return mean mabsl. for the reservoir."""
        mean_vol = self.current_volume + 0.5 * delta_volume
        if mean_vol > self.max_volume:
            mean_vol = self.max_volume

        if self.is_ocean:
            return 0.0
        else:
            # mean_vol = round(mean_vol, 3) # Had some numerical issues with volume beeing slightly above max
            return self.head.get_head(mean_vol)

    def report_state(self, state):
        if self.is_ocean:
            return

        state[self.name] = self.current_volume
        state[ReportName.spillage + self.spillage.get_name()] = self.spillage.get_value()
        state[ReportName.water_value + self.name] = 0.0  # to be monkeypatched in evaluation loop

    def report(self):
        if not self.is_ocean:
            print(self.inflow_model)
        head_str = "None"
        if self.head:
            print(self.head)
            head_str = "head"
        rep_str = '{3} = Res(name="{3}", min_volume={0:.9f}, max_volume={1:.9f}, init_volume={2:.9f}, end_volume={4:.9f},'.format(
            self.min_volume, self.max_volume, self.init_volume, self.name, self.end_volume
        )
        rep_str += " inflow_model=inflow_model, is_ocean={0}, head={1}, energy_equivalent={2})".format(
            self.is_ocean, head_str, self.energy_equivalent
        )
        print(rep_str)


class Station(HSComponent):
    def __init__(self, name, minimum, maximum, gen_func, energy_equivalent):
        self.name = name
        self.input = 0
        self.min = minimum  # [m3/s]
        self.max = maximum  # [m3/s]
        self.gen_func = gen_func
        self.energy_equivalent = energy_equivalent  # [kWh/m3]

        self.discharge = 0
        self.head = 0
        self.production = 0

    def power(self, discharge=None, head=None):

        self.discharge = discharge  # , 3) # Numerical issues NB! Fix
        self.head = head or self.head
        self.production = self.gen_func.get_power(self.discharge, self.head)

        return self.production

    def reset(self):
        self.discharge = 0
        self.head = 0
        self.production = 0

    def get_name(self):
        return self.name

    def get_value(self):
        return self.input

    def report_state(self, state):
        state[ReportName.power + self.name] = self.production
        state[ReportName.discharge + self.name] = self.discharge

    def report(self):
        print(self.gen_func)
        rep_str = '{name} = {cls_name}(name="{name}", minimum={minimum:.9f}, '.format(
            cls_name=type(self).__name__, minimum=self.min, name=self.name
        )
        rep_str += "maximum={maximum:.9f}, gen_func=gen_func,".format(maximum=self.max)
        rep_str += "energy_equivalent={en_eq})".format(en_eq=self.energy_equivalent)
        print(rep_str)


class PickGateAction(HSComponent):
    def __init__(self, name, input_actions):
        self.name = name
        self.input_actions = input_actions
        self.reward = 0
        self.last_actions = None
        self.last_dec_action = 0

    def execute(self, actions, price, step_size):
        raise ValueError("PickGateAction method execute not to be called.")

    def recommend(self):
        """Used for primer policy."""
        rec = []
        for a in self.input_actions:
            rec = rec + a.recommend()
        return rec

    def reset(self):
        self.reward = 0
        for a in self.input_actions:
            a.reset()

    def get_name(self):
        return self.name

    def get_value(self):
        return self.reward

    def report_state(self, state):
        action_index = np.argmax(self.last_actions)
        state[ReportName.picked_gate + self.name] = action_index
        state[ReportName.reward + self.name] = self.input_actions[action_index].reward
        state[ReportName.decision_gate + self.name] = self.last_dec_action
        for a in self.input_actions:
            a.report_state(state)

    def report(self):
        for a in self.input_actions:
            a.report()
        args = "[" + ", ".join(a.name for a in self.input_actions) + "]"
        print(
            '{name} = {cls_name}(name="{name}", input_actions={args})'.format(
                name=self.name, args=args, cls_name=type(self).__name__
            )
        )


class DischargeAction(HSComponent):
    def __init__(self, name, upper_res: Res, lower_res: Res, max_flow):
        self.name = name
        self.upper_res = upper_res
        self.lower_res = lower_res
        self.max_flow = max_flow  # [m3/s]
        self.reward = 0.0

    def recommend(self):
        raise NotImplementedError()

    def reset(self):
        self.reward = 0.0

    def get_name(self):
        return self.name

    def get_value(self):
        return self.reward

    def report_state(self, state):
        state[ReportName.reward + self.name] = self.reward

    def report(self):
        print(
            '{name} = {cls_name}(name="{name}", upper_res={u_res}, lower_res={l_res}, max_flow={max_flow})'.format(
                name=self.name,
                u_res=self.upper_res.name,
                l_res=self.lower_res.name,
                cls_name=type(self).__name__,
                max_flow=self.max_flow,
            )
        )

    def execute(self, discharge, price, step_size):
        self.reward = 0.0

        # Upper reservoir
        discharge_volume = discharge * step_size * 3.6 / 1e3

        if self.upper_res.current_volume - discharge_volume < self.upper_res.min_volume:  # Empty
            # empty_vol = self.upper_res.min_volume - (self.upper_res.current_volume - discharge_volume)
            # self.reward -= empty_vol * price * self.upper_res.energy_equivalent * 10**3
            discharge_volume = (
                self.upper_res.current_volume - self.upper_res.min_volume
            )  # Consider using this for small reservoirs?

        self.upper_res.current_volume -= discharge_volume

        # Spillage
        upper_spill = max(self.upper_res.current_volume - self.upper_res.max_volume, 0.0)
        if upper_spill > 1e-6:
            self.upper_res.current_volume = self.upper_res.max_volume
            self.upper_res.spillage.add_value(upper_spill)

        # Lower reservoir
        self.lower_res.current_volume = discharge_volume + self.lower_res.current_volume

        return self.reward


class StationAction(HSComponent):
    def __init__(self, name, upper_res: Res, station: Station, lower_res: Res):
        self.name = name
        self.upper_res = upper_res
        self.station = station
        self.lower_res = lower_res
        self.reward = 0.0

    def recommend(self):
        raise NotImplementedError()

    def reset(self):
        self.reward = 0.0

    def get_name(self):
        return self.name

    def get_value(self):
        return self.reward

    def report_state(self, state):
        state[ReportName.reward + self.name] = self.reward

    def report(self):
        print(
            '{name} = {cls_name}(name="{name}", upper_res={u_res}, station={station}, lower_res={l_res})'.format(
                name=self.name,
                u_res=self.upper_res.name,
                station=self.station.name,
                l_res=self.lower_res.name,
                cls_name=type(self).__name__,
            )
        )

    def execute(self, discharge, price, step_size):
        self.reward = 0.0

        if discharge > self.station.max:
            discharge = self.station.max
        elif discharge < self.station.min:
            discharge = 0.0

        discharge_volume = discharge * step_size * 3.6 / 1e3  # [Mm3]

        # Upper reservoir
        if self.upper_res.current_volume - discharge_volume < self.upper_res.min_volume:  # Empty
            # Punishment for wanting to produce non-existent water
            # empty_vol = self.upper_res.min_volume - (self.upper_res.current_volume - discharge_volume)
            # self.reward -=  empty_vol * price * self.upper_res.energy_equivalent * 10**3  # [Mm3 * EUR/MWh * kWh/m3 * 1/k]

            # discharge_volume = max(self.upper_res.current_volume - self.upper_res.min_volume, 0)
            # discharge = discharge_volume /step_size / 3.6 * 1E3

            discharge = 0.0  # TODO: How to handle this case??
            discharge_volume = 0.0  # TODO: How to handle this case??

        upper_head = self.upper_res.get_head(-discharge_volume)
        self.upper_res.current_volume -= discharge_volume

        # Spillage
        upper_spill = max(self.upper_res.current_volume - self.upper_res.max_volume, 0.0)
        if upper_spill > 0.0:
            self.upper_res.spillage.add_value(upper_spill)
            self.upper_res.current_volume = self.upper_res.max_volume

        # Lower reservoir
        if not self.lower_res.is_ocean:
            new_volume = discharge_volume + self.lower_res.current_volume

            # Spillage
            spill = max(new_volume - self.lower_res.max_volume, 0.0)
            if spill > 0.0:
                discharge_volume = 0.0  # Max head if lower reservoir is spilling

            lower_head = self.lower_res.get_head(discharge_volume)
            self.lower_res.current_volume = new_volume
            head = upper_head - lower_head

        else:
            head = upper_head

        # Power Station Production
        power_prod = self.station.power(discharge, head) * step_size * price  # [EUR]
        self.reward += power_prod

        return self.reward

    def execute_no_discharge(self):
        # Upper reservoir
        # Spillage
        upper_spill = max(self.upper_res.current_volume - self.upper_res.max_volume, 0.0)
        if upper_spill > 0.0:
            self.upper_res.spillage.add_value(upper_spill)
            self.upper_res.current_volume = self.upper_res.max_volume

        return 0.0


class Spill(HSComponent):
    def __init__(self, name, to_node: Res, price_of_spillage):
        self.name = name
        self.to_node = to_node
        self.value = 0.0
        self.price_of_spillage = price_of_spillage
        self.reward = 0.0

    def reset(self):
        self.value = 0.0
        self.reward = 0.0

    def add_value(self, value):
        self.to_node.current_volume += value  # Add spillage to downstream component
        self.value += value

    def get_value(self):
        return self.value

    def get_name(self):
        return self.name

    def report_state(self, state):
        state[ReportName.reward + self.name] = self.reward

    def execute(self, energy_equivalent):
        self.reward = -self.price_of_spillage * self.value * energy_equivalent * 10**3  # [EUR]
        return self.reward


class VariableInflowAction(HSComponent):
    def __init__(self, name, res: Res, yearly_inflow):
        self.name = name
        self.res = res
        self.yearly_inflow = yearly_inflow  # Remove
        self.reward = 0.0
        self.inflow = 0.0

    def execute(self, price, inflow_this_step, step_size):
        self.reward = 0

        # Inflow in [m3/s]
        self.inflow = inflow_this_step
        # Inflow in [Mm3]
        self.res.current_volume += self.inflow * step_size * 3.6 / 1e3

        return self.reward

    def reset(self):
        self.reward = 0

    def get_name(self):
        return self.name

    def get_value(self):
        return self.reward

    def report_state(self, state):
        pass

    def report(self):
        print(
            '{2} = VariableInflowAction(name="{2}", res={0}, yearly_inflow={1:.9f})'.format(
                self.res.name, self.yearly_inflow, self.name
            )
        )


class HSystem:

    MaxAction, MinAction = 0.9, 0.1  # --SB-- Range 0.1 - 0.9 works better than 0.3-0.7 (and 0.05 - 0.95)
    PickActionCutoff = 0.5

    def __init__(self, reservoirs, stations, sorted_actions):
        assert len([res.name for res in reservoirs]) == len(
            set([res.name for res in reservoirs])
        ), "Reservoirs has not unqiue names"
        self.reservoirs: List[Res] = reservoirs
        self.stations: List[Station] = stations
        self.sorted_actions = sorted_actions
        self.maximum_volume = max([res.max_volume for res in self.reservoirs if not res.is_ocean])  # [Mm3]
        self.maximum_production = max([ps.gen_func.p_max for ps in self.stations])  # [MW]

    def reset(self):
        for res in self.reservoirs:
            res.reset()
        for station in self.stations:
            station.reset()
        for act in self.sorted_actions:
            act.reset()

    def get_num_actions(self):
        counter = 0
        for a in self.sorted_actions:
            if isinstance(a, StationAction):
                counter += 1
            elif isinstance(a, PickGateAction):
                counter += len(a.input_actions) + 1
            elif isinstance(a, DischargeAction):
                counter += 1
        return counter

    def calc_discharge(self, action, min_discharge, max_discharge):
        if action > HSystem.MaxAction:
            return max_discharge
        if action < HSystem.MinAction:
            return 0.0

        action = (action - HSystem.MinAction) / (HSystem.MaxAction - HSystem.MinAction)
        return min_discharge + (max_discharge - min_discharge) * action

    def execute(self, actions, step_size, price, inflows):
        reward = 0.0
        action_index = 0

        for res in self.reservoirs:
            if not res.is_ocean:
                res.spillage.reset()

        # Actions
        for a in self.sorted_actions:
            if isinstance(a, StationAction):

                discharge = self.calc_discharge(actions[action_index], a.station.min, a.station.max)
                reward += a.execute(discharge, price, step_size=step_size)

                action_index += 1
            elif isinstance(a, PickGateAction):
                num_actions = len(a.input_actions)
                pick_actions = actions[action_index : action_index + num_actions]
                dec_action = actions[action_index + num_actions]

                # Use action with highest value
                sel_action_index = np.argmax(pick_actions)
                pick_station = a.input_actions[sel_action_index].station
                discharge = self.calc_discharge(pick_actions[sel_action_index], pick_station.min, pick_station.max)

                # If gate state value is less than a value, it is in an "off" state -> No discharge
                if dec_action < HSystem.PickActionCutoff:
                    discharge = 0.0

                reward += a.input_actions[sel_action_index].execute(discharge, price, step_size)

                # Invoke the other stations with zero discharge
                # Here we need to call execute with 0 discharge to ensure spillage calc works
                for a_idx, aa in enumerate(a.input_actions):
                    if a_idx != sel_action_index:
                        reward += a.input_actions[a_idx].execute_no_discharge()

                a.last_actions = pick_actions
                a.last_dec_action = dec_action

                action_index += num_actions + 1
            elif isinstance(a, VariableInflowAction):
                reward += a.execute(price, inflows[a.res.name], step_size=step_size)

            elif isinstance(a, DischargeAction):

                discharge = self.calc_discharge(actions[action_index], 0.0, a.max_flow)
                reward += a.execute(discharge, price, step_size=step_size)

                action_index += 1
            else:
                reward += a.execute(price)

        # Spillage
        for res in self.reservoirs:
            if not res.is_ocean:
                reward += res.spillage.execute(res.energy_equivalent)

        return reward

    def report_state(self, actions):
        """
        :param actions: Actions provided by the agent.
        """
        state = {}

        for res in self.reservoirs:
            res.report_state(state)

        for stat in self.stations:
            stat.report_state(state)

        action_index = 0
        for a in self.sorted_actions:
            a.report_state(state)
            if isinstance(a, StationAction):
                val = actions[action_index]
                state[ReportName.agent + a.name] = val
                action_index += 1
            elif isinstance(a, DischargeAction):
                val = actions[action_index]
                state[ReportName.agent + a.name] = val
                action_index += 1
            elif isinstance(a, PickGateAction):
                sub_actions = actions[action_index : action_index + len(a.input_actions)]
                used_action = np.argmax(sub_actions)

                for sub_index, sub_a in enumerate(a.input_actions):
                    val = actions[action_index]
                    state[ReportName.agent + sub_a.name] = val
                    action_index += 1

                # Increment for dec action
                action_index += 1

        return state

    def report(self):
        print("#Reservoirs")
        for r in self.reservoirs:
            r.report()
            print()
        print("#Stations")
        for r in self.stations:
            r.report()
            print()
        print("#Actions")
        for r in self.sorted_actions:
            r.report()

        actions = "[" + ", ".join(a.name for a in self.sorted_actions) + "]"
        res = "[" + ", ".join(a.name for a in self.reservoirs) + "]"
        stat = "[" + ", ".join(a.name for a in self.stations) + "]"

        print()
        print("reservoirs = {0}".format(res))
        print("stations = {0}".format(stat))
        print("actions = {0}".format(actions))

        report_str = "system = HSystem(reservoirs=reservoirs, stations=stations, sorted_actions=actions)"
        print(report_str)
