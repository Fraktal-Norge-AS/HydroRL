from enum import Enum


class EndStateIncentive(str, Enum):
    MeanEnergyPrice = "MeanEnergyPrice"
    Off = "Off"
    LastEnergyPrice = "LastEnergyPrice"
    ProvidedEndEnergyPrice = "ProvidedEndEnergyPrice"
    QValue = "QValue"
