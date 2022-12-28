# Basics

The aim of reinforcement learning (RL) algorithms is to maximize or minimize some objective function for an agent operating the given environment. This is done by learning some function based on trial and error. The function can for instance be the policy function, that aims to tell the agent what action it should take, given the current state. It could also be to learn a value function, that provides a value or score for being in a given state. Thus, the agent can use this function to decided which action it should take to such that it can transition to a new high valued state.

At the end of this section we suggest some references to further dvelve into the realm of reinforcement learning. Now, lets look at the basics of a group of RL models.

# Actor-Critic Basics

Actor-critic models refer to RL models that learn both the policy and value function. Where the policy can be seen as the actor, and the value function as the critic, working together achive the defined objective. 

A common objective is to maximize the expected sum of rewards,

$$
J(\pi) = \sum_{t=0}^T \mathbf{E}_{(s_t,a_t)\sim\rho_{\pi}}[r(s_t,a_t)]. 
$$

Where $\rho_{\pi}(s_t,a_t)$ is the state-action marginals of the trajectory distribution induced by a policy $\pi(a_t\vert s_t)$. That is the mapping of $s_t$ and $a_t$ to $s_{t+1}$.

## Exploration vs. Exploitation
A challange with RL models is to decide whether to explore new states and actions, or to exploit the knowledge one already has. To post an illustrative example; you go to you favourite restaurant, open up the menu and have to decide if you should order what you already know is your favourite meal, or if you should try something else. If you try something else, you risk getting dissapointed but you could also discover a meal that you find better than your current favourite. 

Some RL models are prone to being satisfied too early, i.e. not searching enough of the state-action space. The Soft Actor Critic (SAC) algorithm includes an entropy term, aimed at improving the models exploration,

$$
J(\pi) = \sum_{t=0}^T \mathbf{E}_{(s_t,a_t)\sim\rho_{\pi}}[r(s_t,a_t) + \alpha H(\pi(\cdot \vert s_t))]
$$

where the entropy function is defined as

$$
H(P) = -\int_x P(x)\log(P(x)) dx 
$$

The entropy function is an representation of the average suprise. In cases where the policy is not clear what to do, such as the case if the policy is described by a uniform distribution, the entropy function would yield a higher value than if the policy is certain what it should do. The agent is thus incentiviced to explore more, and less on exploiting the current policy.

The temperature parameter $\alpha$ determines the relative importance of the entropy term, and hence the stochasticity of the policy. 

The optimal policy is given as the policy that maximizes $J(\pi)$

$$
\pi^*  = \arg \max_{\pi} J(\pi).
$$

The state value function is defined as

$$
V(s_{t}) = E_{(s_t,a_t) \sim \rho_{\pi}}[\sum_{\tau=0}^\infty (r(s_\tau, a_\tau)+ \alpha H(\pi(\cdot\vert s_\tau))) \vert s_0 = s_t],
$$

and the state-action value function is defined as

$$
Q(s_{t}, a_t) = E_{(s_t,a_t) \sim \rho_{\pi}}[\sum_{\tau=0}^\infty (r(s_\tau, a_\tau) + \sum_{\tau=1}^\infty \alpha H(\pi(\cdot\vert s_\tau))) \vert s_0=s_t, a_0=a_t].
$$

The relationships between the state value function and state-action value function can thus be connected as

$$
V(s_{t}) = E_{a_{t} \sim \pi}[Q(s_t, a_t)] + \alpha H(\pi(\cdot \vert s_t))
$$

and the bellman equation for $Q$ is

$$
Q(s_t, a_t) = E_{(s_{t+1}, a_{t+1}) \sim \rho_{\pi}} [(r(s_t, a_t) + (Q(s_{t+1}, a_{t+1}) + \alpha H(\pi(\cdot\vert s_{t+1}))].
$$

$$
Q(s_t, a_t)= E_{(s_{t+1}) \sim \rho_{\pi}} [r(s_t, a_t) + V(s_{t+1})].
$$

The aim is now to approximate the state-action value and the policy by neural networks. Hence

$$
Q_\theta(s_t,a_t) \approx Q(s_t, a_t)
$$

$$
\pi_\phi(\cdot \vert s_t) = \pi_\phi(f_{\phi}(\epsilon_t;s_t),s_t) \approx \pi(\cdot \vert s_t)
$$

Where the parameters of the neural networks are represented by $\theta$ and $\phi$. The policy makes us of the reparameterization trick, where the policy is dependent on some noise vector $\epsilon_t$ to represent the policy' stocasticity.

## Training of the actor network
If we have $Q(s_t, a_t)$, we can use it to train the policy/actor network.

$$
\nabla_\phi J_\pi(\phi) = \nabla_\phi E_{s_t \sim D, \epsilon \sim N} [Q_\theta(s_t, \pi_\phi(f_\phi(\epsilon_t;s_t)\vert s_t) + \alpha H(\pi_\phi(f_\phi(\epsilon_t;s_t)\vert s_t)]
$$

The network parameters is thus updated by a gradient step

$$
\theta = \theta + \tau_\pi \nabla_\theta J_\pi(\theta).
$$

Where $D$ is a set of previous sampled states, actions and rewards, known as a replay buffer. 

Note that the learning of the actor is highly dependent on how good the state-action value approximation is. Thus, if the state-action value is poor, the policy will also most likely be poor. Furthermore, if the policy is poor the visited states will be far from the optimal ones resulting in slow or no learning. It is sort of a chicken and egg conundrum, solved by taking actions that are incentiviced to explore unknown states. 

## Training of the critic network
Now we just have to find $Q_\theta(s_t, a_t)$. We do this by minizming the bellmann error, $\delta_Q$. 

$$
\hat{Q_\theta} = Q_\theta(s_{t+1},a_{t+1}) + \alpha H(\pi_\theta(\cdot \vert s_{t+1}))
$$

$$
\delta_Q(\phi) = Q_\theta(s_t, a_t) + r_{t+1} - \hat{Q_\theta}
$$

$$
\nabla_\phi J_Q(\phi) = \nabla_\phi \delta_Q(\phi).
$$

And parameters are updated by a gradient step

$$
\phi = \phi + \tau_Q \nabla_\phi J_Q(\phi)
$$


# Additional Resources

For the curious reader we recommend the following resources to further enhance the understanding of reinforcement learning

* [Open AI Spinning Up](https://spinningup.openai.com/en/latest/spinningup/rl_intro.html)
    * A great website with alot of resources to dive into RL
* [DeepMinds YouTube Channel](https://www.youtube.com/channel/UCP7jMXSY2xbc3KCAE0MHQ-A)
    * Containing documentaries, lecture talks and more.
* Articles demonstrating usage of reinforcement learning applied to hydro power scheduling
    * {cite}`Riemer2020`, {cite}`Matheussen2019`
* The reinforcement learning *bible*
    * {cite}`sutton2018`


## Bibliography

```{bibliography}
````
