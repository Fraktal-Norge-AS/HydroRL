from enum import Enum, auto
from abc import ABCMeta, abstractmethod
from typing import Tuple

import numpy as np


class Noise(str, Enum):
    Off = "Off"
    StandardDev = "StandardDev"
    White = "White"


class INoise(metaclass=ABCMeta):
    @abstractmethod
    def sample(self):
        pass


class StandardDevNoise(INoise):
    def __init__(self, std_dev, noise_generator):
        self.mu = 0
        self.std_dev = std_dev
        self.size = std_dev.shape
        self.noise_generator = noise_generator

    def sample(self):
        return self.noise_generator.normal(loc=self.mu, scale=self.std_dev, size=self.size)


class NoNoise(INoise):
    def __init__(self, dims: Tuple):
        self.std_dev = np.zeros_like(dims)

    def sample(self):
        return self.std_dev
