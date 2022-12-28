
def test_unit_conversions():
    
    secs_per_hour  = 3600 # [s/h]
    q_min = 30 # m3/s
    q_max = 60 # m3/s
    base_episode_hours = 365*24 # [h/base_episode]
    episode_hours = 2*365*24 # [h/episode]
    max_max_volume = 45 # [Mm3]
    n_steps = 100 # steps/episode

    base_line = max_max_volume * 1e6 # m3

    min_gen = secs_per_hour * q_min  # m3/h
    max_gen = secs_per_hour * q_max  # m3/h

    min_gen *= base_episode_hours # m3/episode 
    max_gen *= base_episode_hours # m3/episode

    min_gen /= base_line # vol.pu./episode
    max_gen /= base_line # vol.pu./episode

    min_gen /= n_steps # vol.eq/step
    max_gen /= n_steps # vol.eq/step
    
    factor_to_m3s = base_line/(secs_per_hour*base_episode_hours) # m3/((s/h)*h/episode) => (m3/s)*episode
    factor_to_m3s *= n_steps  # m3/s

    assert min_gen * factor_to_m3s == q_min
    assert max_gen * factor_to_m3s == q_max

    # When the episode length is not the same as the base episode length
    # The base episode length is made with 8760 h. (see run_hps_rl.py) 
    episode_scaling = episode_hours/base_episode_hours
    
    assert (min_gen * episode_scaling) * (factor_to_m3s / episode_scaling) == q_min
    assert (max_gen * episode_scaling) * (factor_to_m3s / episode_scaling) == q_max