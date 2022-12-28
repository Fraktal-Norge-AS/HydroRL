from hps.rl.environment.hscomponents import (
    Res,
    Station,
    VariableInflowAction,
    PickGateAction,
    HSystem,
    StationAction,
    DischargeAction,
    Spill,
)
from hps import HydroSystem, Discharge, Reservoir, Gate


class HydroRLBuilder:
    @staticmethod
    def Build(hydro_system: HydroSystem):

        reservoirs = {}
        inflow_actions = {}
        actions = []

        if hydro_system.creeks:
            raise NotImplementedError("Creek not implemented in 'HSystem'")

        spill = dict()
        for spi in hydro_system.spillages:
            spill[spi.parent] = Spill(
                "spill_" + spi.parent.name + "->" + spi.child.name,
                spi.child,
                price_of_spillage=spi.parent.price_of_spillage,
            )

        for res in hydro_system.reservoirs:
            reservoirs[res.name] = Res(
                res.name,
                res.min_volume,
                res.max_volume,
                0.0,
                0.0,
                spill.pop(res),
                res.inflow_model,
                is_ocean=False,
                head=res.head,
                energy_equivalent=res.energy_equivalent,
            )

            inflow_actions[res.name] = VariableInflowAction(
                name="inflow_" + res.name, res=reservoirs[res.name], yearly_inflow=res.inflow_model.mean_yearly_inflow
            )
            actions.append(inflow_actions[res.name])

        if spill:
            raise ValueError("All spillage variables has not beend distributed.")

        for ocean in hydro_system.oceans:
            reservoirs[ocean.name] = Res(ocean.name, 0, 10000.0, 0, 0, None, None, True)

        stations = {}
        for station in hydro_system.power_stations:

            gen_fun = station.generation_function
            stations[station.name] = Station(
                name=station.name,
                minimum=gen_fun.q_min,
                maximum=gen_fun.q_max,
                gen_func=gen_fun,
                energy_equivalent=station.energy_equivalent,
            )

            print("{0}  {1:.5f} {2:.5f}".format(station.name, gen_fun.q_min, gen_fun.q_max))

        for gate in hydro_system.gates:
            upper_reservoirs = [f.parent.name for f in hydro_system.my_edges if f.child.name == gate.name]
            station = [f.child.name for f in hydro_system.my_edges if f.parent.name == gate.name]
            assert len(station) == 1
            station = stations[station[0]]

            lower_res = [f.child.name for f in hydro_system.my_edges if f.parent.name == station.name]
            assert len(lower_res) == 1
            lower_res = lower_res[0]

            power_station_actions = [
                StationAction(i + "_" + station.name + "_" + lower_res, reservoirs[i], station, reservoirs[lower_res])
                for i in upper_reservoirs
            ]

            pick_action = PickGateAction(gate.name, power_station_actions)
            actions.append(pick_action)

        for edge in hydro_system.my_edges:
            if isinstance(edge, Discharge):
                if isinstance(edge.child, Reservoir) and isinstance(edge.parent, Reservoir):

                    upper_res = reservoirs[edge.parent.name]
                    lower_res = reservoirs[edge.child.name]
                    name = edge.parent.name + "_" + edge.child.name
                    actions.append(
                        DischargeAction(name=name, upper_res=upper_res, lower_res=lower_res, max_flow=edge.max_flow)
                    )

        for ps in hydro_system.power_stations:
            upper_reservoirs = [f.parent for f in hydro_system.my_edges if f.child.name == ps.name]
            assert len(upper_reservoirs) == 1
            upper_res = upper_reservoirs[0]
            if isinstance(upper_res, Gate):
                continue

            lower_res = [f.child for f in hydro_system.my_edges if f.parent.name == ps.name]
            assert len(lower_res) == 1
            lower_res = lower_res[0]

            name = upper_res.name + "_" + ps.name + "_" + lower_res.name
            actions.append(
                StationAction(name=name, upper_res=upper_res, station=stations[ps.name], lower_res=lower_res)
            )

        return HSystem(list(reservoirs.values()), list(stations.values()), actions)
