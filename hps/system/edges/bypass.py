from typing import Optional, Union

import numpy as np

from hps.system.edges.base_edge import BaseHydroEdge
from hps.system.nodes import Reservoir, Creek, Ocean


class Bypass(BaseHydroEdge):
    """
    Class defining flow of bypass from reservoir.
    """

    def __init__(
        self,
        parent: Union[Reservoir, Creek],
        child: Union[Reservoir, Creek, Ocean],
        min_flow: float = 0.0,
        max_flow: float = np.inf,
        name: Optional[str] = None,
    ):
        super().__init__(parent, child, min_flow, max_flow, name)

    def __str__(self):
        return "Bypass: {}".format(self.name)
