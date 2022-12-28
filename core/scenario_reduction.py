import numpy as np
from scipy.spatial import distance


def fast_forward_selection_algo(scenarios: np.ndarray, n_reduced_scenarios: int):
    """
    Fast forward algorithm by Heimsch & Romisch 2003.
    :param scenarios: the intial set of scenarios to reduce. (n_scenarios x n_variables)
    :param n_reduced_scenarios: the amount of scenarios to reduce to.
    :returns: A tuple with reduced scenarios and their weight.
    """
    n_scen = scenarios.shape[0]

    J = [i for i in range(n_scen)]  # All nodes in the scenarios
    S = []  # Set of nodes with reduced scenarios

    # Equiprobability for each scenario
    p = np.full((n_scen), 1 / n_scen)
    prob = p

    # Cost matrix/euclidian distance
    cost_matrix = distance.cdist(scenarios, scenarios)

    # Compute probability distances between each scenario and all other scenarios
    prob_distribution = np.dot(p, cost_matrix)

    # Select first scenario to keep, then one with the smalles prob_distribution
    u = prob_distribution.argmin()
    p[u] = 0  # set prob of that to 0

    J.remove(u)
    S.append(u)  # add that node to the reduced scenarios

    for k in range(1, n_reduced_scenarios):
        for i in J:  # from node i in J
            for j in J:  # to node j in J
                cost_matrix[i, j] = min(cost_matrix[i, j], cost_matrix[i, u])
        prob_distribution = np.dot(p, cost_matrix)
        u = prob_distribution.argmin()  # Should exclude columns with indices in S
        p[u] = 0

        J.remove(u)
        S.append(u)

    # Reduced Scenarios
    RS = scenarios[S, :]

    # Calculate the optimal probabilities of the preserved scenarios using the optimal redistribution rule
    P = np.full((n_reduced_scenarios), 1 / n_scen)

    # Calculate the euclidian distance between the scenario node and the reduced node
    dist = distance.cdist(scenarios, RS)

    # Add the probability of the reduced node to itself
    for k in range(n_reduced_scenarios):
        P[k] = prob[S[k]]

    for j in J:  # Loop over all scenario nodes except the reduced nodes
        idx = dist[j, :].argmin()  # Find index of the reduced node closest to this node
        P[idx] = P[idx] + prob[j]  # Add the prob weight from this node to the reduced node

    # Sort numerical issues
    RS = np.array([np.round(i, 6) for i in RS])
    P = [np.round(i, 6) for i in P]

    if sum(P) != 1:
        P = np.array([float(i + 1.0 / len(P) * (1.0 - sum(P))) for i in P])  # Add rest over all

    return RS, P
