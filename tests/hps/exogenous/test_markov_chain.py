import pytest

import numpy as np

from core.markov_chain import MarkovChain
from core.noise import Noise


@pytest.fixture()
def values():

    n_stages = 2
    n_scenarios = 4
    n_features = 2
    
    data = np.array([[
        [1., 3.],
        [2., 2.],
        [2., 3.],
        [1., 3.]],
       [[1., 1.],
        [2., 2.],
        [3., 3.],
        [3., 3.]]])
    
    assert data.shape == (n_stages, n_scenarios, n_features)
    return data
    

@pytest.fixture()
def mc(values):
    n_clusters=2
    return MarkovChain(data=values, n_clusters=n_clusters)

@pytest.fixture()
def mc_white(values):
    n_clusters=2
    return MarkovChain(data=values, n_clusters=n_clusters, sample_noise=Noise.White)

@pytest.fixture()
def mc_std_dev(values):
    n_clusters=2
    return MarkovChain(data=values, n_clusters=n_clusters, sample_noise=Noise.StandardDev)


def test_white(mc_white):
    mc_white.fit()
    nodes, values = mc_white.sample()
    assert nodes.shape[0] == values.shape[0]

def test_std_dev(mc_std_dev):
    mc_std_dev.fit()
    nodes, values = mc_std_dev.sample()
    assert nodes.shape[0] == values.shape[0]

def test_constructor(mc):
    assert mc.n_stages==2
    assert mc.n_features==2



def test_fit(mc):
    mc.fit()

    expected_cluster_centers = (
        np.array([[1. , 3. ], [2. , 2.5]]),
        np.array([[3. , 3.], [1.5, 1.5]])
    )

    actual_cluster_centers = mc.cls_[0].cluster_centers_, mc.cls_[1].cluster_centers_

    np.testing.assert_equal(np.sort(actual_cluster_centers[0], axis=0), np.sort(expected_cluster_centers[0], axis=0))
    np.testing.assert_equal(np.sort(actual_cluster_centers[1], axis=0), np.sort(expected_cluster_centers[1], axis=0))

    expected_transition_matrix = [np.zeros((2,2))+0.5]
    np.testing.assert_equal(mc.transition_matrix_, expected_transition_matrix)

def test_sample(mc):

    n_clusters = 2
    n_features = 2
    init_clusters = [
        np.array([[1. , 3. ], [2. , 2.5]]),
        np.array([[3. , 3.], [1.5, 1.5]])
    ]

    mc.fit(init_clusters=init_clusters)  # Init cluster to get persistent cluster centers

    idx, values = mc.sample(initial_node=0, uniform_sample=0.4) # Choose 0 as next node

    expected_idx = np.array([0, 0])
    expected_values = np.array([[1. , 3.], [3. , 3. ]])

    np.testing.assert_equal(idx, expected_idx)
    np.testing.assert_equal(values, expected_values)

    idx, values = mc.sample(initial_node=0, uniform_sample=0.6) # Choose 1 as next node

    expected_idx = np.array([0, 1])
    expected_values = np.array([[1. , 3.], [1.5 , 1.5 ]])

    np.testing.assert_equal(idx, expected_idx)
    np.testing.assert_equal(values, expected_values)

def test_random_initial_node(mc):
    a=2
    mc.fit()
    trans = mc.transition_matrix_[0]
    print(trans)
    assert True


def dummy():

#%%
    from sklearn.datasets import make_blobs
    from sklearn.cluster import KMeans
    import matplotlib.pyplot as plt
    import numpy as np
    features, true_labels = make_blobs(
        n_samples=2000,
        centers=3,
        cluster_std=2.75,
        random_state=42
    )
# %%

    plt.scatter(features[:,0], features[:,1])

    kmeans = KMeans(n_clusters=3)
# %%
    kmeans.fit(features)
# %%
    plt.scatter(features[:,0], features[:,1])
    plt.scatter(kmeans.cluster_centers_[:,0], kmeans.cluster_centers_[:,1], color='r')
    
# %%
    np.sqrt(kmeans.inertia_/2000)

# %%
    kmeans.labels_
    kmeans.inertia_
    SSE = 0.0
    for i, val in enumerate(features):
        SSE += (kmeans.cluster_centers_[kmeans.labels_[i]]- val)**2

    # SSE = SSE.sum()

    print(SSE, kmeans.inertia_)
    np.sqrt(SSE/(2000-1))

# %%

    cntr = kmeans.labels_[0]
    kmeans.cluster_centers_[cntr]
# %%
    np.array([1,2])- np.array([3,2])
# %%
    random_gen = np.random.Generator(np.random.PCG64(42))
# %%
    random_gen.normal(np.zeros(2), np.array([1,10]))
# %%

    np.sqrt(np.sum((features - kmeans.cluster_centers_[kmeans.labels_])**2, axis=0)/2000)

# %%
