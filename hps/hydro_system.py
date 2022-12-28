"""
Module defining the hydro system class.
"""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Optional, Iterable, Tuple, Callable, Union, List, Type

import networkx as nx
from networkx.algorithms.link_analysis.hits_alg import hits

from hps.system.nodes import IHydroNode, Reservoir, Creek, Ocean, PowerStation, Gate
from hps.system.edges import IHydroEdge, Discharge, Spillage, Bypass


class HydroSystem(nx.MultiDiGraph):
    """
    Class defining the hydro system.
    """

    def __init__(
        self,
        name: str = "",
        nodes: Optional[Iterable[IHydroNode]] = None,
        edges: Optional[Iterable[IHydroEdge]] = None,
        **attr,
    ) -> None:
        """Constructor method.

        :param name: Name of the hydro system, defaults to ""
        :type name: str, optional
        :param nodes: Iterable of nodes in the system, defaults to None
        :type nodes: Optional[Iterable[IHydroNode]], optional
        :param edges: Iterable of edges in the system, defaults to None
        :type edges: Optional[Iterable[IHydroEdge]], optional
        """
        super().__init__(self, **attr)

        self.name = name
        if nodes:
            self.add_nodes_from(nodes)
        if edges:
            self.add_edges_from(edges)

    def to_dict(self):
        """Method used to serialize the hydro system.

        :return: Serialized hydro system
        :rtype: dict
        """
        dct = dict()
        dct["name"] = self.name
        dct["reservoirs"] = [res.to_dict() for res in self.reservoirs]
        dct["power stations"] = [ps.to_dict() for ps in self.power_stations]
        dct["oceans"] = [ocean.to_dict() for ocean in self.oceans]
        dct["creeks"] = [creek.to_dict() for creek in self.creeks]
        dct["gates"] = [gate.to_dict() for gate in self.gates]

        dct["discharges"] = [dis.to_dict() for dis in self.discharges]
        dct["spillages"] = [spi.to_dict() for spi in self.spillages]
        dct["bypasses"] = [byp.to_dict() for byp in self.bypasses]

        return {type(self).__name__: dct}

    def add_edge(self, edge: IHydroEdge):
        """Add edge to the hydro system.

        Note that the nodes in the edge has to be defined in the hydro system.

        :param edge: Edge to add in the hydro system
        :type edge: IHydroEdge
        :raises ValueError: If a node is not defined in the hydro system
        """
        u = edge.parent
        v = edge.child

        if u in self.nodes and v in self.nodes and isinstance(edge, IHydroEdge):
            super(HydroSystem, self).add_edge(u, v, conn=edge)
        else:
            raise ValueError("A node in edge {} not defined in the hydro system.".format(edge))

    def add_node(self, node: IHydroNode):
        """Add node to the hydro system.

        :param node: Node to add in the hydro system
        :type node: IHydroNode
        :raises ValueError: If the node is not of type IHydroNode or it is already defined in the hydro system
        """
        if isinstance(node, IHydroNode):
            intersect = set([node.name for node in self.nodes]).intersection(set([node.name]))
            if intersect:
                raise ValueError(
                    f"Node name has to be unique. '{intersect}' already exists in hydro system. {node.name}"
                )
            super(HydroSystem, self).add_node(node)
        else:
            raise ValueError("Unknown node.")

    def add_nodes_from(self, nodes: Iterable[IHydroNode]):
        """Add a iterable of nodes to the hydro system.

        :param nodes: Iterable of nodes to add
        :type nodes: Iterable[IHydroNode]
        """
        for node in nodes:
            self.add_node(node)

    def add_edges_from(self, edges: Iterable[IHydroEdge]):
        """Add a iterable of edges to the hydro system.

        :param edges: Iterable of edges to add
        :type edges: Iterable[IHydroEdge]
        """
        for edge in edges:
            self.add_edge(edge)

    @property
    def my_edges(self) -> List:
        """
        :return: Edges
        :rtype: List
        """
        return [d["conn"] for _, _, d in self.edges(data=True)]

    @property
    def my_nodes(self) -> List:
        """
        :return: Nodes
        :rtype: List
        """
        return [node for node in self.nodes()]

    @property
    def reservoirs(self) -> List[Reservoir]:
        """
        :return: Reservoirs
        :rtype: List[Reservoir]
        """
        return [node for node in self.nodes if isinstance(node, Reservoir)]

    @property
    def power_stations(self) -> List[PowerStation]:
        """
        :return: Power stations
        :rtype: List[PowerStation]
        """
        return [node for node in self.nodes if isinstance(node, PowerStation)]

    @property
    def gates(self) -> List[Gate]:
        """
        :return: Gates
        :rtype: List[Gate]
        """
        return [node for node in self.nodes if isinstance(node, Gate)]

    @property
    def creeks(self) -> List[Creek]:
        """
        :return: Creeks
        :rtype: List[Creek]
        """
        return [node for node in self.nodes if isinstance(node, Creek)]

    @property
    def oceans(self) -> List[Ocean]:
        """
        :return: Oceans
        :rtype: List[Ocean]
        """
        return [node for node in self.nodes if isinstance(node, Ocean)]

    @property
    def discharges(self) -> List[Discharge]:
        """
        :return: Discharges
        :rtype: List[Discharge]
        """
        return [d["conn"] for _, _, d in self.edges(data=True) if isinstance(d["conn"], Discharge)]

    @property
    def bypasses(self) -> List[Bypass]:
        """
        :return: Bypasses
        :rtype: List[Bypass]
        """
        return [d["conn"] for _, _, d in self.edges(data=True) if isinstance(d["conn"], Bypass)]

    @property
    def spillages(self) -> List[Spillage]:
        """
        :return: Spillages
        :rtype: List[Spillage]
        """
        return [d["conn"] for _, _, d in self.edges(data=True) if isinstance(d["conn"], Spillage)]

    def get_subgraph(self, edge_type: Type[IHydroEdge] = Discharge) -> HydroSystem:
        """Get a subgraph containing only edges with a given type.

        :param edge_type: The required edge type, defaults to :class:`Discharge`
        :type edge_type: Type[IHydroEdge], optional
        :return: A subgraph of the hydro system
        :rtype: HydroSystem
        """
        edges: Iterable[IHydroEdge] = [
            d["conn"] for (u, v, d) in self.edges(data=True) if isinstance(d["conn"], edge_type)
        ]
        nodes: Iterable[IHydroNode] = list(
            set([node for edges in edges for node in [edges.parent, edges.child]])
        )  # Only unique nodes

        system = HydroSystem()
        system.add_nodes_from(nodes)
        system.add_edges_from(edges)

        return system


class HydroSystemPostCalculations:
    """
    Class defining methods used for post calculations on a hydro system.
    """

    @staticmethod
    def compute_reservoir_energy_equivalents(hydro_system: HydroSystem):
        """
        Assign energy equivalent values to reserveroirs.
        Values are populated from ocean and up the system.

        :param hydro_system: A hydro system instance
        :type hydro_system: HydroSystem
        """
        for ps in hydro_system.power_stations:
            if ps.energy_equivalent is None:
                raise ValueError(f"Energy equivalent missing in {ps.name}")

        hs = hydro_system.get_subgraph(edge_type=Discharge)

        # Find paths from source to sinks
        sink_nodes = [node for node, outdegree in hs.out_degree() if outdegree == 0]
        source_nodes = [node for node, indegree in hs.in_degree() if indegree == 0]
        source_to_sink = [(source, sink) for sink in sink_nodes for source in source_nodes]

        discharge_paths = []
        for source, sink in source_to_sink:
            for path in nx.all_simple_paths(hs, source=source, target=sink):
                discharge_paths.append(path)

        for path in discharge_paths:
            current_energy_eq = 0
            for node in reversed(path):  # Start from sink/ocean
                if isinstance(node, Reservoir) or isinstance(node, PowerStation):
                    if isinstance(node, Reservoir):
                        node.energy_equivalent = current_energy_eq
                    elif isinstance(node, PowerStation):
                        current_energy_eq += node.energy_equivalent  # Accumulate energy eq. up the system
