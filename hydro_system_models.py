#%%
from hps.utils.function_approx import LinearFunctionApprox
from hps import (
    Reservoir, Creek, Ocean, Gate, PowerStation, HydroSystem,
    Discharge, Spillage, Bypass)
from hps.system.inflow import SimpleInflowModel, ScaleYearlyInflowModel
from hps import HydroSystem
from hps.system.nodes import Reservoir, PowerStation, Ocean, Gate
from hps.system.edges import Bypass, Discharge, Spillage
from hps.system.head_function import LinearHeadFunction, ExpHeadFunction
from hps.system.generation_function.generation_head_function import (
    VanillaGenerationHeadFunction)
from hps.system.generation_function import ConstantGenerationFunction

from hps.system.head_function.base_head_function import ConstantHeadFunction

def hydro_system_small():
    inflow_mod1 = ScaleYearlyInflowModel(mean_yearly_inflow=200)
    
    res1_head = ConstantHeadFunction(430, 0, 205)
    # res1_head = ExpHeadFunction(400, 450, 0, 205, decay=0.01)
    res1 = Reservoir(
        "res1", 0, 205, inflow_model=inflow_mod1,
        head=res1_head, tank_water_cost=50)
    
    h = 430
    rho = 1e3  # [kg/m3]
    g = 9.81  # [m/s2]
    n = 80.  # [-]
    C = n/100*rho*g/1e6
    p_min, p_max = 60, 180
    q_min, q_max = p_min/(C*h), p_max/(C*h)

    eff_func = LinearFunctionApprox(
        x=[17.77967428, 19.65121894, 21.5227636 , 23.39430826, 25.26585292, 27.13739758, 29.00894224, 30.8804869 , 32.75203156, 34.62357622, 36.49512088, 38.36666554, 40.2382102 , 42.10975487, 43.98129953, 45.85284419, 47.72438885, 49.59593351, 51.46747817, 53.33902283],
        y=[72.      , 72.298345, 72.68423 , 73.157992, 73.719336, 74.368514, 75.105316, 75.929911, 76.842172, 77.842183, 78.883408, 79.689537, 80.213942, 80.456893, 80.417984, 80.097755, 79.495532, 78.612124, 77.446587, 76.])
    gen_func1 = VanillaGenerationHeadFunction(q_min, q_max, p_min, p_max, eff_func)
    
    ps1 = PowerStation("ps1", 3e4, False, generation_function=gen_func1, nominal_discharge=q_max*0.8, nominal_head=h)
    ocean = Ocean("ocean")

    dis1 = Discharge(res1, ps1)
    dis2 = Discharge(ps1, ocean)
    spi = Spillage(res1, ocean)

    return HydroSystem(
        nodes=[res1, ps1, ocean],
        edges=[dis1, dis2, spi]
    )


def hydro_system_medium():
    """Lysebotn"""
    hydro_system = HydroSystem()

    # Nilsebuvatnet    
    res1_head = LinearHeadFunction(717.4, 731.4, 0, 40.5)
    res1 = Reservoir(
        "res1", 0, 40.5, inflow_model=ScaleYearlyInflowModel(mean_yearly_inflow=400),
        head = res1_head, tank_water_cost = 50)

    # Lyngsvatn    
    res2_head = ExpHeadFunction(636.4, 686.4, 0, 515.6, decay=0.01)
    res2 = Reservoir(
        "res2", 0, 515.6, inflow_model=ScaleYearlyInflowModel(mean_yearly_inflow=200),
        head = res2_head, tank_water_cost = 40
    ) 

    # Strandvatn    
    res3_head = LinearHeadFunction(618.6, 634.6, 0, 22.3)
    res3 = Reservoir(
        "res3", 0, 22.3, inflow_model=ScaleYearlyInflowModel(mean_yearly_inflow=300),
        head = res3_head, tank_water_cost = 40
    ) 
    
    switch = Gate("switch")

    # Breiava
    h = (717.4 + 731.4)/2 - (658. + 693)/2  # [m]
    rho = 1e3  # [kg/m3]
    g = 9.81  # [m/s2]
    n = 80.  # [-]
    C = n/100*rho*g/1e6
    p_min, p_max = 14, 27
    q_min, q_max = p_min/(C*h), p_max/(C*h)

    eff = LinearFunctionApprox(x=[q_min, q_max], y=[n, n])
    gen_func_1 = VanillaGenerationHeadFunction(q_min, q_max, p_min, p_max, eff)
    ps1 = PowerStation("ps1", 4e4, initial_state=False, generation_function=gen_func_1, nominal_discharge=q_max*0.8, nominal_head=h)
    
    # Lysebotn-2
    h = 630
    p_min, p_max = 50, 420
    q_min, q_max = p_min/(C*h), p_max/(C*h)

    eff = LinearFunctionApprox(x=[q_min, 0.8*q_max, q_max], y=[75., 85., 82.])
    gen_func_2 = VanillaGenerationHeadFunction(q_min, q_max, p_min, p_max, eff)
    ps2 = PowerStation("ps2", 2e4, initial_state=False, generation_function=gen_func_2, nominal_discharge=q_max*0.8, nominal_head=h)

    ocean1 = Ocean("ocean1")
    ocean2 = Ocean("ocean2")

    hydro_system.add_nodes_from([
        res1, res2, res3, switch, ps1, ps2, ocean1, ocean2
    ])

    hydro_system.add_edges_from([
        Discharge(res1, ps1, max_flow=27),
        Discharge(ps1, res2, max_flow=27),
        Discharge(res2, switch, max_flow=60),
        Discharge(res3, switch, max_flow=60),
        Discharge(switch, ps2, max_flow=60),
        Discharge(ps2, ocean1, max_flow=60),
        Spillage(res1, ocean2),
        Spillage(res2, ocean1),
        Spillage(res3, ocean1)
    ])

    return hydro_system

def hydro_system_large():
    """Sira-Kvina"""
    hydro_system = HydroSystem()
    
    # Sira
    res1_head = LinearHeadFunction(lrv=780, hrv=899, v_min=0, v_max=1398)
    res1 = Reservoir("res1", 0, 1398, inflow_model=ScaleYearlyInflowModel(mean_yearly_inflow=1398/2.92), head=res1_head) # Svartevatn
    
    res2_head = LinearHeadFunction(lrv=625, hrv=660, v_min=0, v_max=312+39)
    res2 = Reservoir("res2", 0, 312+39, inflow_model=ScaleYearlyInflowModel(mean_yearly_inflow=(312+39)/0.39), head=res2_head) # Gravvatn
    
    res3_head = LinearHeadFunction(lrv=482, hrv=497.6, v_min=0, v_max=12)
    res3 = Reservoir("res3", 0, 12, inflow_model=ScaleYearlyInflowModel(mean_yearly_inflow=12/0.04), head=res3_head) # Ousdalsvatn    

    #Kvina
    res4_head = LinearHeadFunction(lrv=890, hrv=929, v_min=0, v_max=684)
    res4 = Reservoir("res4", 0, 684, inflow_model=ScaleYearlyInflowModel(mean_yearly_inflow=684/1.33), head=res4_head) # Roskrepp
    
    res5_head = LinearHeadFunction(lrv=820, hrv=837, v_min=0, v_max=104)
    res5 = Reservoir("res5", 0, 104, inflow_model=ScaleYearlyInflowModel(mean_yearly_inflow=104/0.46), head=res5_head) # Øyarvatn
    
    res6_head = LinearHeadFunction(lrv=677, hrv=715, v_min=0, v_max=274)
    res6 = Reservoir("res6", 0, 274, inflow_model=ScaleYearlyInflowModel(mean_yearly_inflow=274/0.48), head=res6_head) # Kvifjorden
    
    res7_head = LinearHeadFunction(lrv=471, hrv=497.6, v_min=0, v_max=55)
    res7 = Reservoir("res7", 0, 55, inflow_model=ScaleYearlyInflowModel(mean_yearly_inflow=55/0.21), head=res7_head)  # Homstølvatn

    switch1 = Gate("switch1")

    res8_head = LinearHeadFunction(lrv=44, hrv=49.5, v_min=0, v_max=161)
    res8 = Reservoir("res8", 0, 161, inflow_model=ScaleYearlyInflowModel(mean_yearly_inflow=161/0.17), head=res8_head) #Sirdalsvatn
    ocean = Ocean("ocean")
    
    station1_gen = ConstantGenerationFunction(50, 200, 2.0) # 2 x 100 MW Francis
    station1 = PowerStation("station1", 4e4, initial_state=False, generation_function=station1_gen, nominal_discharge=200/2) # Duge

    station2_gen = ConstantGenerationFunction(30, 120, 60/42) # 2 x 60 MW Francis
    station2 = PowerStation("station2", 2e4, initial_state=False, generation_function=station2_gen, nominal_discharge=120/(60/42)) # Tjørhom
    
    station3_gen = ConstantGenerationFunction(25, 50, 50/70) # 50 MW Francis
    station3 = PowerStation("station3", 2e4, initial_state=False, generation_function=station3_gen, nominal_discharge=70) # Roskrepp
    
    station4_gen = ConstantGenerationFunction(40, 80, 80/77) # 80 MW Francis
    station4 = PowerStation("station4", 2e4, initial_state=False, generation_function=station4_gen, nominal_discharge=77) # Kvinen
    
    station5_gen = ConstantGenerationFunction(50, 200, 200/110) # 2 x 100 MW Francis
    station5 = PowerStation("station5", 2e4, initial_state=False, generation_function=station5_gen, nominal_discharge=110) # Solhom
    
    station6_gen = ConstantGenerationFunction(80, 960, 960/165) # 4 x 160 + 1 x 320 MW Francis
    station6 = PowerStation("station6", 2e4, initial_state=False, generation_function=station6_gen, nominal_discharge=165) # Tonstad
    
    station7_gen = ConstantGenerationFunction(25, 150, 150/375) 
    station7 = PowerStation("station7", 2e4, initial_state=False, generation_function=station7_gen, nominal_discharge=375) # Åna-Sira
    
    hydro_system.add_nodes_from([
        res1, res2, res3, res4, res5, res6, res7, res8, switch1, station1, station2, station3, station4, station5, station6, station7, ocean
    ])

    hydro_system.add_edges_from([
        Discharge(res1, station1, max_flow=100),
        Discharge(station1, res2, max_flow=100),
        Discharge(res2, station2, max_flow=84),
        Discharge(station2, res3, max_flow=84),

        Discharge(res4, station3, max_flow=70),
        Discharge(station3, res5, max_flow=70),
        Discharge(res5, station4, max_flow=77),
        Discharge(station4, res6, max_flow=77),        
        Discharge(res6, station5, max_flow=110),
        Discharge(station5, res7, max_flow=110),

        Discharge(res3, switch1, max_flow=165),
        Discharge(res7, switch1, max_flow=165),
        Discharge(switch1, station6, max_flow=165),
        Discharge(station6, res8,  max_flow=165),
        Discharge(res8, station7, max_flow=375),
        Discharge(station7, ocean, max_flow=375),

        Spillage(res1, res2),
        Spillage(res2, res3),
        Spillage(res3, res8),
        Spillage(res4, res5),
        Spillage(res5, res6),
        Spillage(res6, res7),
        Spillage(res7, res8),
        Spillage(res8, ocean)
    ])

    return hydro_system

def hydro_system_with_creek():
    # Hydro system
    inflow_mod1 = SimpleInflowModel(mean_yearly_inflow=200, series_id="10")
    inflow_mod2 = SimpleInflowModel(mean_yearly_inflow=100, series_id="10")
    inflow_mod3 = SimpleInflowModel(mean_yearly_inflow=30, series_id="11")
    inflow_mod4 = SimpleInflowModel(mean_yearly_inflow=10, series_id="11")

    res1 = Reservoir("res1", 0, 200, inflow_model=inflow_mod1)
    res2 = Reservoir("res2", 0, 350, inflow_model=inflow_mod2)
    res3 = Reservoir("res3", 0, 20, inflow_model=inflow_mod3)
    creek = Creek("creek", inflow_model=inflow_mod4)
    gate = Gate("gate")

    gen_func1 = ConstantGenerationFunction(60, 180, 2.5)
    gen_func2 = ConstantGenerationFunction(100, 250, 2.8)

    ps1 = PowerStation("ps1", 3e4, False, generation_function=gen_func1)
    ps2 = PowerStation("ps2", 3e4, False, generation_function=gen_func2)
    ocean = Ocean("ocean")

    dis0 = Discharge(creek, res3, 0, 60)
    dis1 = Discharge(res1, ps1,)
    dis2 = Discharge(ps1, res2)
    dis3 = Discharge(res2, gate)
    dis4 = Discharge(res3, gate)
    dis5 = Discharge(gate, ps2)
    dis6 = Discharge(ps2, ocean)

    spi = Spillage(res1, res2)
    spi1 = Spillage(creek, ocean)
    spi2 = Spillage(res3, ocean)
    spi3 = Spillage(res2, ocean)

    byp = Bypass(res3, res2)

    return HydroSystem(
        nodes=[creek, res1, res2, res3, ps1, ps2, gate, ocean],
        edges=[dis0, dis1, dis2, dis3, dis4, dis5, dis6, spi, spi1, spi2, spi3, byp]
    )

def hydro_system():
    # Hydro system
    inflow_mod1 = SimpleInflowModel(mean_yearly_inflow=200, series_id="10")
    inflow_mod2 = SimpleInflowModel(mean_yearly_inflow=100, series_id="10")
    inflow_mod3 = SimpleInflowModel(mean_yearly_inflow=40, series_id="11")
    
    max_price = 20
    res1 = Reservoir("res1", 0, 200, inflow_model=inflow_mod1)
    res1.twa_cost = max_price*2
    res2 = Reservoir("res2", 0, 350, inflow_model=inflow_mod2)
    res2.twa_cost = max_price
    res3 = Reservoir("res3", 0, 20, inflow_model=inflow_mod3)
    res3.twa_cost = max_price
    
    gate = Gate("gate")

    gen_func1 = ConstantGenerationFunction(60, 180, 2.5)
    gen_func2 = ConstantGenerationFunction(100, 250, 2.8)

    ps1 = PowerStation("ps1", 3e4, False, generation_function=gen_func1)
    ps2 = PowerStation("ps2", 3e4, False, generation_function=gen_func2)
    ocean = Ocean("ocean")

    dis1 = Discharge(res1, ps1,)
    dis2 = Discharge(ps1, res2)
    dis3 = Discharge(res2, gate)
    dis4 = Discharge(res3, gate)
    dis5 = Discharge(gate, ps2)
    dis6 = Discharge(ps2, ocean)

    spi = Spillage(res1, res2)
    spi2 = Spillage(res3, ocean)
    spi3 = Spillage(res2, ocean)

    byp = Bypass(res3, res2)

    return HydroSystem(
        nodes=[res1, res2, res3, ps1, ps2, gate, ocean],
        edges=[dis1, dis2, dis3, dis4, dis5, dis6, spi, spi2, spi3, byp]
    )