#%%
from hps.system.head_function import LinearHeadFunction, ExpHeadFunction
from hps.system.head_function.base_head_function import HeadFunction, ConstantHeadFunction
from hps.system.generation_function.generation_head_function import (
    VanillaGenerationHeadFunction, GenerationHeadFunction)
from hps.system.generation_function.constant import ConstantGenerationFunction

from hps.system.inflow import ScaleInflowModel, ScaleYearlyInflowModel
from hps.utils.function_approx import LinearFunctionApprox

from hps.rl.environment.hscomponents import (
    HSystem, Res, Station, PickGateAction, Spill,
    VariableInflowAction, StationAction, DischargeAction)

class HSGen:
    @staticmethod
    def create_system(name : str, start_volume, price_of_spillage, use_linear_model):
        env = None
        if name == "large":
            if use_linear_model:
                env = HSGen.create_large_linear(start_volume, price_of_spillage)
            else:
                env = HSGen.create_large(start_volume, price_of_spillage)
        if name == "medium":
            if use_linear_model:
                env = HSGen.create_medium_linear(start_volume, price_of_spillage)
            else:
                env = HSGen.create_medium(start_volume, price_of_spillage)
        elif name == "small":
            if use_linear_model:
                env = HSGen.create_small_linear(start_volume, price_of_spillage)    
            else:
                env = HSGen.create_small(start_volume, price_of_spillage)
        

        if env is None:
            raise ValueError("No such system :'" + name + "'")

        return env

    @staticmethod
    def create_large(start_volume, price_of_spillage):
        #Reservoirs
        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=478.76712328767127)
        head = LinearHeadFunction(lrv=780, hrv=899, v_min=0, v_max=1398)
        res1 = Res(name="res1", min_volume=0.000000000, max_volume=1398.000000000, init_volume=start_volume["res1"], end_volume=700.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=2.67965367965368)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=900)
        head = LinearHeadFunction(lrv=625, hrv=660, v_min=0, v_max=351)
        res2 = Res(name="res2", min_volume=0.000000000, max_volume=351.000000000, init_volume=start_volume["res2"], end_volume=100.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=2.1240981240981243)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=300)
        head = LinearHeadFunction(lrv=482, hrv=497.6, v_min=0, v_max=12)
        res3 = Res(name="res3", min_volume=0.000000000, max_volume=12.000000000, init_volume=start_volume["res3"], end_volume=10.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=1.7272727272727273)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=514.2857142857142)
        head = LinearHeadFunction(lrv=890, hrv=929, v_min=0, v_max=684)
        res4 = Res(name="res4", min_volume=0.000000000, max_volume=684.000000000, init_volume=start_volume["res4"], end_volume=200.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=2.7193362193362196)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=226.08695652173913)
        head = LinearHeadFunction(lrv=820, hrv=837, v_min=0, v_max=104)
        res5 = Res(name="res5", min_volume=0.000000000, max_volume=104.000000000, init_volume=start_volume["res5"], end_volume=50.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=2.520923520923521)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=570.8333333333334)
        head = LinearHeadFunction(lrv=677, hrv=715, v_min=0, v_max=274)
        res6 = Res(name="res6", min_volume=0.000000000, max_volume=274.000000000, init_volume=start_volume["res6"], end_volume=150.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=2.2323232323232323)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=261.9047619047619)
        head = LinearHeadFunction(lrv=471, hrv=497.6, v_min=0, v_max=55)
        res7 = Res(name="res7", min_volume=0.000000000, max_volume=55.000000000, init_volume=start_volume["res7"], end_volume=30.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=1.7272727272727273)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=947.0588235294117)
        head = LinearHeadFunction(lrv=44, hrv=49.5, v_min=0, v_max=161)
        res8 = Res(name="res8", min_volume=0.000000000, max_volume=161.000000000, init_volume=start_volume["res8"], end_volume=90.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=0.1111111111111111)

        ocean = Res(name="ocean", min_volume=0.000000000, max_volume=10000.000000000, init_volume=0, end_volume=0.000000000, spillage=None, inflow_model=inflow_model, is_ocean=True, head=None, energy_equivalent=None)
        
        res1.spillage = Spill(res1.name+ "-" + res2.name, res2, price_of_spillage)
        res2.spillage = Spill(res2.name+ "-" + res3.name, res3, price_of_spillage)
        res3.spillage = Spill(res3.name+ "-" + res8.name, res8, price_of_spillage)
        res4.spillage = Spill(res4.name+ "-" + res5.name, res5, price_of_spillage)
        res5.spillage = Spill(res5.name+ "-" + res6.name, res6, price_of_spillage)
        res6.spillage = Spill(res6.name+ "-" + res7.name, res7, price_of_spillage)
        res7.spillage = Spill(res7.name+ "-" + res8.name, res8, price_of_spillage)
        res8.spillage = Spill(res8.name+ "-" + ocean.name, ocean, price_of_spillage)

        #Stations
        gen_func = ConstantGenerationFunction(p_min=50.0, p_max=200.0, power_equivalent=2.0)
        station1 = Station(name="station1", minimum=25.000000000, maximum=100.000000000, gen_func=gen_func, energy_equivalent=0.5555555555555556)

        gen_func = ConstantGenerationFunction(p_min=30.0, p_max=120.0, power_equivalent=1.4285714285714286)
        station2 = Station(name="station2", minimum=21.000000000, maximum=84.000000000, gen_func=gen_func, energy_equivalent=0.3968253968253968)

        gen_func = ConstantGenerationFunction(p_min=25.0, p_max=50.0, power_equivalent=0.7142857142857143)
        station3 = Station(name="station3", minimum=35.000000000, maximum=70.000000000, gen_func=gen_func, energy_equivalent=0.1984126984126984)

        gen_func = ConstantGenerationFunction(p_min=40.0, p_max=80.0, power_equivalent=1.0389610389610389)
        station4 = Station(name="station4", minimum=38.500000000, maximum=77.000000000, gen_func=gen_func, energy_equivalent=0.2886002886002886)

        gen_func = ConstantGenerationFunction(p_min=50.0, p_max=200.0, power_equivalent=1.8181818181818181)
        station5 = Station(name="station5", minimum=27.500000000, maximum=110.000000000, gen_func=gen_func, energy_equivalent=0.5050505050505051)

        gen_func = ConstantGenerationFunction(p_min=80.0, p_max=960.0, power_equivalent=5.818181818181818)
        station6 = Station(name="station6", minimum=13.750000000, maximum=165.000000000, gen_func=gen_func, energy_equivalent=1.6161616161616161)

        gen_func = ConstantGenerationFunction(p_min=25.0, p_max=150.0, power_equivalent=0.4)
        station7 = Station(name="station7", minimum=62.500000000, maximum=375.000000000, gen_func=gen_func, energy_equivalent=0.1111111111111111)

        #Actions
        inflow_res1 = VariableInflowAction(name="inflow_res1", res=res1, yearly_inflow=478.767123288)
        inflow_res2 = VariableInflowAction(name="inflow_res2", res=res2, yearly_inflow=900.000000000)
        inflow_res3 = VariableInflowAction(name="inflow_res3", res=res3, yearly_inflow=300.000000000)
        inflow_res4 = VariableInflowAction(name="inflow_res4", res=res4, yearly_inflow=514.285714286)
        inflow_res5 = VariableInflowAction(name="inflow_res5", res=res5, yearly_inflow=226.086956522)
        inflow_res6 = VariableInflowAction(name="inflow_res6", res=res6, yearly_inflow=570.833333333)
        inflow_res7 = VariableInflowAction(name="inflow_res7", res=res7, yearly_inflow=261.904761905)
        inflow_res8 = VariableInflowAction(name="inflow_res8", res=res8, yearly_inflow=947.058823529)
        res3_station6_res8 = StationAction(name="res3_station6_res8", upper_res=res3, station=station6, lower_res=res8)
        res7_station6_res8 = StationAction(name="res7_station6_res8", upper_res=res7, station=station6, lower_res=res8)
        switch1 = PickGateAction(name="switch1", input_actions=[res3_station6_res8, res7_station6_res8])
        res1_station1_res2 = StationAction(name="res1_station1_res2", upper_res=res1, station=station1, lower_res=res2)
        res2_station2_res3 = StationAction(name="res2_station2_res3", upper_res=res2, station=station2, lower_res=res3)
        res4_station3_res5 = StationAction(name="res4_station3_res5", upper_res=res4, station=station3, lower_res=res5)
        res5_station4_res6 = StationAction(name="res5_station4_res6", upper_res=res5, station=station4, lower_res=res6)
        res6_station5_res7 = StationAction(name="res6_station5_res7", upper_res=res6, station=station5, lower_res=res7)
        res8_station7_ocean = StationAction(name="res8_station7_ocean", upper_res=res8, station=station7, lower_res=ocean)
        
        reservoirs = [res1, res2, res3, res4, res5, res6, res7, res8, ocean]
        stations = [station1, station2, station3, station4, station5, station6, station7]
        actions = [
            inflow_res1, inflow_res2, inflow_res3, inflow_res4, inflow_res5, inflow_res6, inflow_res7, inflow_res8,
            res1_station1_res2, res2_station2_res3, res4_station3_res5, res5_station4_res6, res6_station5_res7, switch1, res8_station7_ocean]

        return HSystem(reservoirs=reservoirs, stations=stations, sorted_actions=actions)

    @staticmethod
    def create_large_linear(start_volume, price_of_spillage):
        #Reservoirs
        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=478.76712328767127)
        # head = LinearHeadFunction(lrv=780, hrv=899, v_min=0, v_max=1398)
        head = ConstantHeadFunction(head=780 + (899-780)/2, v_min=0, v_max=1398)
        res1 = Res(name="res1", min_volume=0.000000000, max_volume=1398.000000000, init_volume=start_volume["res1"], end_volume=700.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=2.67965367965368)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=900)
        # head = LinearHeadFunction(lrv=625, hrv=660, v_min=0, v_max=351)
        head = ConstantHeadFunction(head=625 + (660-625)/2, v_min=0, v_max=351)
        res2 = Res(name="res2", min_volume=0.000000000, max_volume=351.000000000, init_volume=start_volume["res2"], end_volume=100.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=2.1240981240981243)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=300)
        # head = LinearHeadFunction(lrv=482, hrv=497.6, v_min=0, v_max=12)
        head = ConstantHeadFunction(head=482 + (497.6-482)/2, v_min=0, v_max=12)
        res3 = Res(name="res3", min_volume=0.000000000, max_volume=12.000000000, init_volume=start_volume["res3"], end_volume=10.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=1.7272727272727273)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=514.2857142857142)
        # head = LinearHeadFunction(lrv=890, hrv=929, v_min=0, v_max=684)
        head = ConstantHeadFunction(head=890 + (929-890)/2, v_min=0, v_max=684)
        res4 = Res(name="res4", min_volume=0.000000000, max_volume=684.000000000, init_volume=start_volume["res4"], end_volume=200.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=2.7193362193362196)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=226.08695652173913)
        # head = LinearHeadFunction(lrv=820, hrv=837, v_min=0, v_max=104)
        head = ConstantHeadFunction(head=820 + (837-820)/2, v_min=0, v_max=104)
        res5 = Res(name="res5", min_volume=0.000000000, max_volume=104.000000000, init_volume=start_volume["res5"], end_volume=50.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=2.520923520923521)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=570.8333333333334)
        # head = LinearHeadFunction(lrv=677, hrv=715, v_min=0, v_max=274)
        head = ConstantHeadFunction(head=677 + (715-677)/2, v_min=0, v_max=274)
        res6 = Res(name="res6", min_volume=0.000000000, max_volume=274.000000000, init_volume=start_volume["res6"], end_volume=150.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=2.2323232323232323)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=261.9047619047619)
        # head = LinearHeadFunction(lrv=471, hrv=497.6, v_min=0, v_max=55)
        head = ConstantHeadFunction(head=471 + (497.6-471)/2, v_min=0, v_max=55)
        res7 = Res(name="res7", min_volume=0.000000000, max_volume=55.000000000, init_volume=start_volume["res7"], end_volume=30.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=1.7272727272727273)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=947.0588235294117)
        # head = LinearHeadFunction(lrv=44, hrv=49.5, v_min=0, v_max=161)
        head = ConstantHeadFunction(head=44 + (49.5-44)/2, v_min=0, v_max=161)
        res8 = Res(name="res8", min_volume=0.000000000, max_volume=161.000000000, init_volume=start_volume["res8"], end_volume=90.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=0.1111111111111111)

        ocean = Res(name="ocean", min_volume=0.000000000, max_volume=10000.000000000, init_volume=0, end_volume=0.000000000, spillage=None, inflow_model=inflow_model, is_ocean=True, head=None, energy_equivalent=None)

        res1.spillage = Spill(res1.name+ "-" + res2.name, res2, price_of_spillage)
        res2.spillage = Spill(res2.name+ "-" + res3.name, res3, price_of_spillage)
        res3.spillage = Spill(res3.name+ "-" + res8.name, res8, price_of_spillage)
        res4.spillage = Spill(res4.name+ "-" + res5.name, res5, price_of_spillage)
        res5.spillage = Spill(res5.name+ "-" + res6.name, res6, price_of_spillage)
        res6.spillage = Spill(res6.name+ "-" + res7.name, res7, price_of_spillage)
        res7.spillage = Spill(res7.name+ "-" + res8.name, res8, price_of_spillage)
        res8.spillage = Spill(res8.name+ "-" + ocean.name, ocean, price_of_spillage)


        #Stations
        gen_func = ConstantGenerationFunction(p_min=50.0, p_max=200.0, power_equivalent=2.0)
        station1 = Station(name="station1", minimum=25.000000000, maximum=100.000000000, gen_func=gen_func, energy_equivalent=0.5555555555555556)

        gen_func = ConstantGenerationFunction(p_min=30.0, p_max=120.0, power_equivalent=1.4285714285714286)
        station2 = Station(name="station2", minimum=21.000000000, maximum=84.000000000, gen_func=gen_func, energy_equivalent=0.3968253968253968)

        gen_func = ConstantGenerationFunction(p_min=25.0, p_max=50.0, power_equivalent=0.7142857142857143)
        station3 = Station(name="station3", minimum=35.000000000, maximum=70.000000000, gen_func=gen_func, energy_equivalent=0.1984126984126984)

        gen_func = ConstantGenerationFunction(p_min=40.0, p_max=80.0, power_equivalent=1.0389610389610389)
        station4 = Station(name="station4", minimum=38.500000000, maximum=77.000000000, gen_func=gen_func, energy_equivalent=0.2886002886002886)

        gen_func = ConstantGenerationFunction(p_min=50.0, p_max=200.0, power_equivalent=1.8181818181818181)
        station5 = Station(name="station5", minimum=27.500000000, maximum=110.000000000, gen_func=gen_func, energy_equivalent=0.5050505050505051)

        gen_func = ConstantGenerationFunction(p_min=80.0, p_max=960.0, power_equivalent=5.818181818181818)
        station6 = Station(name="station6", minimum=13.750000000, maximum=165.000000000, gen_func=gen_func, energy_equivalent=1.6161616161616161)

        gen_func = ConstantGenerationFunction(p_min=25.0, p_max=150.0, power_equivalent=0.4)
        station7 = Station(name="station7", minimum=62.500000000, maximum=375.000000000, gen_func=gen_func, energy_equivalent=0.1111111111111111)

        #Actions
        inflow_res1 = VariableInflowAction(name="inflow_res1", res=res1, yearly_inflow=478.767123288)
        inflow_res2 = VariableInflowAction(name="inflow_res2", res=res2, yearly_inflow=900.000000000)
        inflow_res3 = VariableInflowAction(name="inflow_res3", res=res3, yearly_inflow=300.000000000)
        inflow_res4 = VariableInflowAction(name="inflow_res4", res=res4, yearly_inflow=514.285714286)
        inflow_res5 = VariableInflowAction(name="inflow_res5", res=res5, yearly_inflow=226.086956522)
        inflow_res6 = VariableInflowAction(name="inflow_res6", res=res6, yearly_inflow=570.833333333)
        inflow_res7 = VariableInflowAction(name="inflow_res7", res=res7, yearly_inflow=261.904761905)
        inflow_res8 = VariableInflowAction(name="inflow_res8", res=res8, yearly_inflow=947.058823529)
        res3_station6_res8 = StationAction(name="res3_station6_res8", upper_res=res3, station=station6, lower_res=res8)
        res7_station6_res8 = StationAction(name="res7_station6_res8", upper_res=res7, station=station6, lower_res=res8)
        switch1 = PickGateAction(name="switch1", input_actions=[res3_station6_res8, res7_station6_res8])
        res1_station1_res2 = StationAction(name="res1_station1_res2", upper_res=res1, station=station1, lower_res=res2)
        res2_station2_res3 = StationAction(name="res2_station2_res3", upper_res=res2, station=station2, lower_res=res3)
        res4_station3_res5 = StationAction(name="res4_station3_res5", upper_res=res4, station=station3, lower_res=res5)
        res5_station4_res6 = StationAction(name="res5_station4_res6", upper_res=res5, station=station4, lower_res=res6)
        res6_station5_res7 = StationAction(name="res6_station5_res7", upper_res=res6, station=station5, lower_res=res7)
        res8_station7_ocean = StationAction(name="res8_station7_ocean", upper_res=res8, station=station7, lower_res=ocean)
        
        reservoirs = [res1, res2, res3, res4, res5, res6, res7, res8, ocean]
        stations = [station1, station2, station3, station4, station5, station6, station7]
        actions = [
            inflow_res1, inflow_res2, inflow_res3, inflow_res4, inflow_res5, inflow_res6, inflow_res7, inflow_res8,
            res1_station1_res2, res2_station2_res3, res4_station3_res5, res5_station4_res6, res6_station5_res7, switch1, res8_station7_ocean]

        return HSystem(reservoirs=reservoirs, stations=stations, sorted_actions=actions)

    @staticmethod
    def create_medium(start_volume, price_of_spillage):
        #Reservoirs
        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=400)
        head = LinearHeadFunction(lrv=717.4, hrv=731.4, v_min=0, v_max=40.5)
        res1 = Res(name="res1", min_volume=0.000000000, max_volume=40.500000000, init_volume=start_volume["res1"], end_volume=20.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=1.4839238451619086)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=200)
        head = ExpHeadFunction(lrv=636.4, hrv=686.4, v_min=0, v_max=515.6)
        res2 = Res(name="res2", min_volume=0.000000000, max_volume=515.600000000, init_volume=start_volume["res2"], end_volume=200.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=1.3773218451619087)
        
        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=300)
        head = LinearHeadFunction(lrv=618.6, hrv=634.6, v_min=0, v_max=22.3)
        res3 = Res(name="res3", min_volume=0.000000000, max_volume=22.300000000, init_volume=start_volume["res3"], end_volume=12.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=1.3773218451619087)

        ocean1 = Res(name="ocean1", min_volume=0.000000000, max_volume=10000.000000000, init_volume=0, end_volume=0.000000000, spillage=None, inflow_model=inflow_model, is_ocean=True, head=None, energy_equivalent=None)

        ocean2 = Res(name="ocean2", min_volume=0.000000000, max_volume=10000.000000000, init_volume=0, end_volume=0.000000000, spillage=None, inflow_model=inflow_model, is_ocean=True, head=None, energy_equivalent=None)

        res1.spillage = Spill(res1.name + "-" + ocean2.name, ocean2, price_of_spillage)
        res2.spillage = Spill(res2.name + "-" + ocean1.name, ocean1, price_of_spillage)
        res3.spillage = Spill(res3.name + "-" + ocean1.name, ocean1, price_of_spillage)        

        #Stations        
        eff = LinearFunctionApprox(x = [36.48044960590693, 70.35515281139193], y = [80., 80.])
        gen_func = VanillaGenerationHeadFunction(q_min=36.48044960590693, q_max=70.35515281139193, p_min=14.0, p_max=27.0, eff=eff)
        ps1 = Station(name="ps1", minimum=36.480449606, maximum=70.355152811, gen_func=gen_func,energy_equivalent=0.10660199999999993)

        eff = LinearFunctionApprox(x=[10.112777696875554, 67.95786612300373, 84.94733265375466], y=[75.0, 85.0, 82.0])
        gen_func = VanillaGenerationHeadFunction(q_min=10.112777696875554, q_max=84.94733265375466, p_min=50.0, p_max=420.0, eff=eff)
        ps2 = Station(name="ps2", minimum=10.112777697, maximum=84.947332654, gen_func=gen_func,energy_equivalent=1.4592374999999995)

        #Actions
        inflow_res1 = VariableInflowAction(name="inflow_res1", res=res1, yearly_inflow=444.444444444)
        inflow_res2 = VariableInflowAction(name="inflow_res2", res=res2, yearly_inflow=645.000000000)
        inflow_res3 = VariableInflowAction(name="inflow_res3", res=res3, yearly_inflow=460.000000000)
        res2_ps2_ocean1 = StationAction(name="res2_ps2_ocean1", upper_res=res2, station=ps2, lower_res=ocean1)
        res3_ps2_ocean1 = StationAction(name="res3_ps2_ocean1", upper_res=res3, station=ps2, lower_res=ocean1)
        switch = PickGateAction(name="switch", input_actions=[res2_ps2_ocean1, res3_ps2_ocean1])
        res1_ps1_res2 = StationAction(name="res1_ps1_res2", upper_res=res1, station=ps1, lower_res=res2)

        reservoirs = [res1, res2, res3, ocean1, ocean2]
        stations = [ps1, ps2]
        actions = [inflow_res2, inflow_res1, inflow_res3, res1_ps1_res2, switch]
        
        system = HSystem(reservoirs=reservoirs, stations=stations, sorted_actions=actions)
        return system

    @staticmethod
    def create_medium_linear(start_volume, price_of_spillage):
        #Reservoirs
        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=400)
        head = ConstantHeadFunction(head=717.4 + (731.4-717.4)/2, v_min=0, v_max=40.5)
        res1 = Res(name="res1", min_volume=0.000000000, max_volume=40.500000000, init_volume=start_volume["res1"], end_volume=20.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=1.4839238451619086)

        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=200)
        head = ConstantHeadFunction(head=636.4 + (686.4-636.4)/2, v_min=0, v_max=515.6)
        res2 = Res(name="res2", min_volume=0.000000000, max_volume=515.600000000, init_volume=start_volume["res2"], end_volume=200.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=1.3773218451619087)
        
        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=300)
        head = ConstantHeadFunction(head=618.6 + (634.6 - 618.6)/2, v_min=0, v_max=22.3)
        res3 = Res(name="res3", min_volume=0.000000000, max_volume=22.300000000, init_volume=start_volume["res3"], end_volume=12.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=1.3773218451619087)

        ocean1 = Res(name="ocean1", min_volume=0.000000000, max_volume=10000.000000000, init_volume=0, end_volume=0.000000000, spillage=None, inflow_model=inflow_model, is_ocean=True, head=None, energy_equivalent=None)

        ocean2 = Res(name="ocean2", min_volume=0.000000000, max_volume=10000.000000000, init_volume=0, end_volume=0.000000000, spillage=None, inflow_model=inflow_model, is_ocean=True, head=None, energy_equivalent=None)

        res1.spillage = Spill(res1.name + "-" + ocean2.name, ocean2, price_of_spillage)
        res2.spillage = Spill(res2.name + "-" + ocean1.name, ocean1, price_of_spillage)
        res3.spillage = Spill(res3.name + "-" + ocean1.name, ocean1, price_of_spillage)
        

        #Stations
        eff = LinearFunctionApprox(x=[0, 70.35515281139193],y=[80., 80.])
        gen_func = VanillaGenerationHeadFunction(q_min=0, q_max=70.35515281139193, p_min=0, p_max=27.0, eff=eff)
        ps1 = Station(name="ps1", minimum=0, maximum=70.355152811, gen_func=gen_func,energy_equivalent=0.10660199999999993)

        eff = LinearFunctionApprox(x=[0.0, 67.95786612300373, 84.94733265375466], y=[85.0, 85.0, 82.0])
        gen_func = VanillaGenerationHeadFunction(q_min=0.0, q_max=84.94733265375466, p_min=50.0, p_max=420.0, eff=eff)
        ps2 = Station(name="ps2", minimum=0.0, maximum=84.947332654, gen_func=gen_func,energy_equivalent=1.4592374999999995)

        #Actions
        inflow_res1 = VariableInflowAction(name="inflow_res1", res=res1, yearly_inflow=444.444444444)
        inflow_res2 = VariableInflowAction(name="inflow_res2", res=res2, yearly_inflow=645.000000000)
        inflow_res3 = VariableInflowAction(name="inflow_res3", res=res3, yearly_inflow=460.000000000)
        res2_ps2_ocean1 = StationAction(name="res2_ps2_ocean1", upper_res=res2, station=ps2, lower_res=ocean1)
        res3_ps2_ocean1 = StationAction(name="res3_ps2_ocean1", upper_res=res3, station=ps2, lower_res=ocean1)
        switch = PickGateAction(name="switch", input_actions=[res2_ps2_ocean1, res3_ps2_ocean1])
        res1_ps1_res2 = StationAction(name="res1_ps1_res2", upper_res=res1, station=ps1, lower_res=res2)

        reservoirs = [res1, res2, res3, ocean1, ocean2]
        stations = [ps1, ps2]
        actions = [inflow_res2, inflow_res1, inflow_res3, res1_ps1_res2, switch]
        
        system = HSystem(reservoirs=reservoirs, stations=stations, sorted_actions=actions)
        return system
    
    @staticmethod
    def create_small(start_volume, price_of_spillage):
        #Reservoirs
        
        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=200)
        head = ConstantHeadFunction(head=430, v_min=0, v_max=205)
        res1 = Res(name="res1", min_volume=0.000000000, max_volume=205.000000000, init_volume=start_volume["res1"], end_volume=100.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=0.9429626538850028)

        ocean = Res(name="ocean", min_volume=0.000000000, max_volume=10000.000000000, init_volume=0, end_volume=0.000000000, spillage=None, inflow_model=inflow_model, is_ocean=True, head=None, energy_equivalent=None)

        res1.spillage = Spill(res1.name + "-" + ocean.name, ocean, price_of_spillage)

        #Stations
        eff = LinearFunctionApprox(
            x=[17.77967428, 19.65121894, 21.5227636 , 23.39430826, 25.26585292, 27.13739758, 29.00894224, 30.8804869 , 32.75203156, 34.62357622, 36.49512088, 38.36666554, 40.2382102 , 42.10975487, 43.98129953, 45.85284419, 47.72438885, 49.59593351, 51.46747817, 53.33902283],
            y=[72.      , 72.298345, 72.68423 , 73.157992, 73.719336, 74.368514, 75.105316, 75.929911, 76.842172, 77.842183, 78.883408, 79.689537, 80.213942, 80.456893, 80.417984, 80.097755, 79.495532, 78.612124, 77.446587, 76.])
        gen_func = VanillaGenerationHeadFunction(q_min=17.779674276367256, q_max=53.339022829101765, p_min=60.0, p_max=180.0, eff=eff)
        ps1 = Station(name="ps1", minimum=17.779674276, maximum=53.339022829, gen_func=gen_func,energy_equivalent=0.9429626538850028)

        #Actions
        inflow_res1 = VariableInflowAction(name="inflow_res1", res=res1, yearly_inflow=200.000000000)
        res1_ps1_ocean = StationAction(name="res1_ps1_ocean", upper_res=res1, station=ps1, lower_res=ocean)
        
        reservoirs = [res1, ocean]
        stations = [ps1]
        actions = [inflow_res1, res1_ps1_ocean]

        return HSystem(reservoirs=reservoirs, stations=stations, sorted_actions=actions)

    @staticmethod
    def create_small_linear(start_volume, price_of_spillage):
        #Reservoirs
        
        inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=200)
        head = ConstantHeadFunction(head=430, v_min=0, v_max=205)
        res1 = Res(name="res1", min_volume=0.000000000, max_volume=205.000000000, init_volume=start_volume["res1"], end_volume=100.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=0.9429626538850028)

        ocean = Res(name="ocean", min_volume=0.000000000, max_volume=10000.000000000, init_volume=0, end_volume=0.000000000, spillage=None, inflow_model=inflow_model, is_ocean=True, head=None, energy_equivalent=None)

        res1.spillage = Spill(res1.name + "-" + ocean.name, ocean, price_of_spillage)

        #Stations
        eff = LinearFunctionApprox(
            x=[0.        , 17.7796    , 17.77967428, 19.65121894, 21.5227636 , 23.39430826, 25.26585292, 27.13739758, 29.00894224, 30.8804869 , 32.75203156, 34.62357622, 36.49512088, 38.36666554, 40.2382102 , 42.10975487, 43.98129953, 45.85284419, 47.72438885, 49.59593351, 51.46747817, 53.33902283],
            y=[80.456893, 80.456893, 80.456893, 80.456893, 80.456893, 80.456893, 80.456893, 80.456893, 80.456893, 80.456893, 80.456893, 80.456893, 80.456893, 80.456893, 80.456893, 80.456893, 80.456893, 80.456893, 80.417984, 80.097755, 79.495532, 78.612124])
        gen_func = VanillaGenerationHeadFunction(q_min=0., q_max=53.339022829101765, p_min=60.0, p_max=180.0, eff=eff)
        ps1 = Station(name="ps1", minimum=0., maximum=53.339022829, gen_func=gen_func,energy_equivalent=0.9429626538850028)

        #Actions
        inflow_res1 = VariableInflowAction(name="inflow_res1", res=res1, yearly_inflow=200.000000000)
        res1_ps1_ocean = StationAction(name="res1_ps1_ocean", upper_res=res1, station=ps1, lower_res=ocean)
        
        reservoirs = [res1, ocean]
        stations = [ps1]
        actions = [inflow_res1, res1_ps1_ocean]

        return HSystem(reservoirs=reservoirs, stations=stations, sorted_actions=actions)
