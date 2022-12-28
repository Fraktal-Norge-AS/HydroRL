from hydro_systems import HSGen

class MyDummyDict:
    """Return a constant value for any key."""
    def __init__(self, value):
        self.value = value
        
    def __getitem__(self, key):
        return self.value
    

def test_hydro_power_systems():

    create_methods = [func for func in dir(HSGen) if callable(getattr(HSGen, func)) and func.startswith("create_") and not func.startswith("create_system")]

    start_volume = MyDummyDict(0)

    for func in create_methods:
        _ = getattr(HSGen, func)(start_volume, price_of_spillage=1)

    assert True


