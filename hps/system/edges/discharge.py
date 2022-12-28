from typing import Optional
import numpy as np

from hps.system.edges.base_edge import BaseHydroEdge
from hps.system.nodes import IHydroNode


class Discharge(BaseHydroEdge):
    """
    Class defining flow of discharge between nodes in the hydro system.
    """

    def __init__(
        self,
        parent: IHydroNode,
        child: IHydroNode,
        min_flow: float = 0.0,
        max_flow: float = np.inf,
        name: Optional[str] = None,
    ):
        super().__init__(parent, child, min_flow, max_flow, name)

    def __str__(self):
        return "Discharge: {}".format(self.name)
