#%%
from dataclasses import dataclass
import tensorflow as tf


def histogram_trainable_critic_variables(critic_weights, step, model_name="Critic"):
    for layer_idx, weights in enumerate(critic_weights):
        nme = weights.name.split("/")
        layer_name = nme[-2]
        weight_type = nme[-1]
        tf.summary.histogram(f"{model_name}/{layer_name}_{layer_idx}_{weight_type}", weights, step=step)


def histogram_trainable_actor_variables(encoding_network_weights, projection_network_weights, step, model_name="Actor"):
    for weights in encoding_network_weights:
        nme = weights.name.split("/")
        layer_name = nme[-2]
        weight_type = nme[-1]
        tf.summary.histogram(f"{model_name}/Encoding_{layer_name}_{weight_type}", weights, step=step)

    for weights in projection_network_weights:
        nme = weights.name.split("/")
        layer_name = nme[-2]
        weight_type = nme[-1]
        tf.summary.histogram(f"{model_name}/Projection_{layer_name}_{weight_type}", weights, step=step)


# %%


@dataclass
class NetworkWeights:
    __slots__ = [
        "c1_weights",
        "c2_weights",
        "c1_target_weights",
        "c2_target_weights",
        "a_encoding_weights",
        "a_projection_weights",
    ]
    c1_weights: list
    c2_weights: list
    c1_target_weights: list
    c2_target_weights: list
    a_encoding_weights: list
    a_projection_weights: list
