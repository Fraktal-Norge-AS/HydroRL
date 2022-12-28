from enum import Enum, IntFlag


class ReportName(str, Enum):
    sum_money = "Sum_money"
    energy_price = "Energy_Price"
    scaled_energy_price = "Scaled_Energy_Price"
    sum_mwh = "Sum_MWh"
    end_q_value = "end_q_value"
    end_value = "end_value"
    inflow = "Inflow_"
    spillage = "Spill_"
    water_value = "WV_"
    power = "Power_"
    discharge = "Discharge_"
    reward = "reward_"
    picked_gate = "picked_"
    decision_gate = "dec_"
    agent = "Agent_"


def filter_report_columns(columns):
    filter = [
        ReportName.inflow,
        ReportName.power,
        ReportName.agent,
        ReportName.discharge,
        ReportName.scaled_energy_price,
        ReportName.end_q_value,
        ReportName.end_value,
        ReportName.water_value,
        ReportName.reward,
    ]
    result = []
    for col in columns:
        if not any([col.startswith(f) for f in filter]):
            result.append(col)
    return result
