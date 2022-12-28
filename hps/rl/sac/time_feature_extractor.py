from enum import Enum
from typing import List, Dict, Union
from gym import spaces
import torch as th
import torch.nn as nn

from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from stable_baselines3.common.utils import get_device
from torch.nn.parameter import Parameter

from hps.rl.environment.observations_generator import LinearTimePeriod
from hps.rl.environment.observations_generator import ObservationsName


class CosineLayer(nn.Module):
    def __init__(self, time_periods: List[float], device: Union[th.device, str] = "auto"):
        super(CosineLayer, self).__init__()

        self.time_periods = time_periods

        if min(time_periods) < 1 or max(time_periods) > 8760 * 5:
            raise ValueError("time_periods should be between [0, 8760*5]")

        device = get_device(device)
        self.w = Parameter(2 * th.pi * th.as_tensor(time_periods, dtype=th.float32, device=device) / 8760)
        self.b = Parameter(th.zeros_like(self.w, dtype=th.float32, device=device))

    def forward(self, time_input: th.Tensor) -> th.Tensor:
        return th.cos(self.w * time_input + self.b)

    def to(self, *args, **kwargs):
        self = super().to(*args, **kwargs)
        self.w = self.w.to(*args, **kwargs)
        self.b = self.b.to(*args, **kwargs)
        return self

    def get_time_periods_and_weights(self):
        return zip(self.time_periods, self.w, self.b)


class TimeFourierFeatureExtractor(BaseFeaturesExtractor):
    """
    :param observation_space: (Space.Dict)
    :param time_periods: (List) List of different time periods.
    """

    def __init__(self, observation_space: spaces.Dict, time_periods: List):
        super(TimeFourierFeatureExtractor, self).__init__(observation_space, features_dim=1)

        total_concat_size = 0
        extractors = {}
        for key, space in observation_space.spaces.items():
            if key == ObservationsName.fourier_time:
                extractors[key] = CosineLayer(time_periods=time_periods)
                total_concat_size += len(time_periods)
            else:
                extractors[key] = nn.Identity(device=get_device())
                total_concat_size += space.shape[0]

        self.extractors = nn.ModuleDict(extractors)
        self._features_dim = total_concat_size  # Update feature dim

    def forward(self, observations: Dict) -> th.Tensor:
        encoded_tensor_list = []

        # self.extractors contain nn.   dsadds Modules that do all the processing.
        for key, extractor in self.extractors.items():
            encoded_tensor_list.append(extractor(observations[key]))
        # Return a (B, self._features_dim) PyTorch tensor, where B is batch dimension.
        return th.cat(encoded_tensor_list, dim=0)


class CombinedIdentityExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space: spaces.Dict):
        super(CombinedIdentityExtractor, self).__init__(observation_space, features_dim=1)
        extractors = {}
        total_concat_size = 0
        for key, subspace in observation_space.spaces.items():
            extractors[key] = nn.Identity()
            total_concat_size += subspace.shape[0]

        self.extractors = nn.ModuleDict(extractors)
        self._features_dim = total_concat_size

    def forward(self, observations) -> th.Tensor:
        encoded_tensor_list = []

        for key, extractor in self.extractors.items():
            encoded_tensor_list.append(extractor(observations[key]))

        return th.cat(encoded_tensor_list, dim=1)


class CustomCombinedExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space: spaces.Dict, *args, **kwargs):
        # We do not know features-dim here before going over all the items,
        # so put something dummy for now. PyTorch requires calling
        # nn.Module.__init__ before adding modules
        super(CustomCombinedExtractor, self).__init__(observation_space, features_dim=1)

        extractors = {}

        total_concat_size = 0
        # We need to know size of the output of this extractor,
        # so go over all the spaces and compute output feature sizes
        for key, subspace in observation_space.spaces.items():
            extractors[key] = nn.Linear(subspace.shape[0], subspace.shape[0])
            total_concat_size += subspace.shape[0]

        self.extractors = nn.ModuleDict(extractors)

        # Update the features dim manually
        self._features_dim = total_concat_size

    def forward(self, observations) -> th.Tensor:
        encoded_tensor_list = []

        # self.extractors contain nn.Modules that do all the processing.
        for key, extractor in self.extractors.items():
            encoded_tensor_list.append(extractor(observations[key]))
        # Return a (B, self._features_dim) PyTorch tensor, where B is batch dimension.
        return th.cat(encoded_tensor_list, dim=1)
