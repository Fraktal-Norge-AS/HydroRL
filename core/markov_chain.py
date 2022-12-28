from typing import AbstractSet, Optional, Tuple, List
from collections import Counter
from abc import ABCMeta, abstractmethod

import numpy as np
from sklearn.cluster import KMeans

from core.noise import StandardDevNoise, NoNoise, Noise, INoise


class IForecastGenerator(metaclass=ABCMeta):
    @abstractmethod
    def sample(self):
        pass

    @abstractmethod
    def fit(self):
        pass

    @abstractmethod
    def set_seed(self, seed):
        pass

    @abstractmethod
    def get_std_dev(self):
        pass


class BaseForecastGenerator(IForecastGenerator):
    def sample(self):
        raise NotImplementedError("To be implemented by subclass")

    def fit(self):
        raise NotImplementedError("To be implemented by subclass")

    def set_seed(self, seed):
        raise NotImplementedError("To be implemented by subclass")

    def get_std_dev(self):
        raise NotImplementedError("To be implemented by subclass")


class MarkovChain(BaseForecastGenerator):
    def __init__(self, data, n_clusters, seed=42, sample_noise: Noise = Noise.Off):
        """
        shape of data: n_stages x n_scenarios x n_features

        """
        self.data = data
        self.n_clusters = n_clusters
        self.n_stages, self.n_scenarios, self.n_features = self.data.shape
        self.random_gen = np.random.Generator(np.random.PCG64(seed))
        self.seed = seed
        self.noise_gen = np.random.Generator(np.random.PCG64(seed))
        self.sample_noise = sample_noise
        self.cls_: List = []
        self.fit()

        if sample_noise == Noise.Off:
            self.noise = NoNoise(dims=(self.n_stages, self.n_features))  # type: INoise
        elif sample_noise == Noise.White:
            self.noise = StandardDevNoise(
                std_dev=np.ones((self.n_stages, self.n_features)), noise_generator=self.noise_gen
            )
        elif sample_noise == Noise.StandardDev:
            self.noise = StandardDevNoise(std_dev=self.get_std_dev(), noise_generator=self.noise_gen)
        else:
            raise ValueError(f"{sample_noise} not a valid Noise instance.")

    def fit(self, init_clusters=None):

        clusters = []
        if isinstance(self.n_clusters, int):
            clusters = [self.n_clusters for i in range(self.n_stages)]
        elif isinstance(self.n_clusters, list):
            clusters = self.n_clusters

        if init_clusters is not None:
            self.cls_ = [
                KMeans(n_clusters=c, init=init_clusters[t], random_state=self.seed) for t, c in enumerate(clusters)
            ]
        else:
            self.cls_ = [KMeans(n_clusters=c, random_state=self.seed) for c in clusters]

        for t, cluster in enumerate(self.cls_):
            try:
                cluster.fit(self.data[t])
            except Exception as e:
                raise type(e)(e.message + f"t: {t}")

        self.transition_matrix_ = []
        for t in range(1, self.n_stages):
            self.transition_matrix_.append(np.zeros((clusters[t - 1], clusters[t])))

            # Count from which cluster the scenarios starts and ends up in
            for i, j in zip(self.cls_[t - 1].labels_, self.cls_[t].labels_):
                self.transition_matrix_[t - 1][i, j] += 1

            # Divide by the sum to get an probability estimate of going from one cluster to the others
            for i in range(clusters[t - 1]):
                self.transition_matrix_[t - 1][i] /= self.transition_matrix_[t - 1][i].sum()

        self.clusters = np.array([cluster.cluster_centers_ for cluster in self.cls_])
        self.max_values = self.clusters.max(axis=1) + self.clusters.min(axis=1)
        self.max_values[:, 0] = np.inf

    def get_std_dev(self):
        if not self.cls_:
            raise ValueError("Markov chain has not been trained.")

        std_dev = np.zeros((self.n_stages, self.n_features))
        for t in range(self.n_stages):
            std_dev[t] = np.sqrt(
                np.sum((self.data[t] - self.cls_[t].cluster_centers_[self.cls_[t].labels_]) ** 2, axis=0)
                / (self.n_features - 1)
            )

        return std_dev

    def _transition_from(self, t: int, current_node: int, uniform_sample):
        sample = uniform_sample or self.random_gen.uniform()
        acc_probs = np.cumsum(self.transition_matrix_[t][current_node])
        for next_node, p in enumerate(acc_probs):
            if sample <= p:
                return next_node, sample

    def _random_initial_node(self, uniform_sample=None):
        sample = uniform_sample or self.random_gen.uniform()

        # Compute prob of starting from an initial node
        count = Counter(self.cls_[0].labels_)
        sorted_count = dict(sorted(count.items()))
        n_values = sum(sorted_count.values())
        probs = np.array([sorted_count[i] / n_values for i in sorted_count])
        acc_probs = np.cumsum(probs)

        for node, p in enumerate(acc_probs):
            if sample <= p:
                return node

    def set_seed(self, seed: int):
        self.random_gen = np.random.Generator(np.random.PCG64(seed))

    def sample(self, initial_node: Optional[int] = None, uniform_sample=None):
        """
        Sample a scenario from the markov chain.

        :param initial_node: Chose initial node in sample. If set to None, a random node is used. Defaults to None
        :param uniform_sample: An optional uniform sample value.
        :return: sampled scenario.
        """
        nodes = np.zeros(self.n_stages, dtype=np.int8)  # type: np.ndarray
        values = np.zeros((self.n_stages, self.n_features))

        t = 0
        if initial_node is None:
            initial_node = self._random_initial_node()
        nodes[t] = initial_node
        values[t] = self.cls_[t].cluster_centers_[initial_node]

        for t in range(self.n_stages - 1):
            nodes[t + 1], _ = self._transition_from(t, nodes[t], uniform_sample)
            values[t + 1] = self.cls_[t + 1].cluster_centers_[nodes[t + 1]]

        values += self.noise.sample()  # Add noise to value

        values = np.clip(values, 0.0, self.max_values)

        return nodes, values
