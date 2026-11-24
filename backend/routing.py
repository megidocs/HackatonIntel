from math import isfinite
from pathlib import Path

import networkx as nx
import numpy as np
import osmnx as ox

DEFAULT_GRAPH_PATH = Path(__file__).parent / "data" / "manhattan.graphml"
MAX_SNAP_METERS = 500


class PointOutsideGraph(ValueError):
    pass


class ManhattanRouter:
    def __init__(self, path: Path):
        if not path.is_file():
            raise RuntimeError(f"Missing road graph at {path}. Run python -m backend.prepare_graph.")
        self.graph = ox.io.load_graphml(path)
        edges = self.graph.edges(data=True)
        max_speed = 0.0
        for _, _, edge in edges:
            for attribute in ("length", "speed_kph", "travel_time"):
                value = edge.get(attribute)
                if value is None or not isfinite(value) or value <= 0:
                    raise RuntimeError(f"Invalid edge {attribute} in {path}. Rebuild the road graph.")
            max_speed = max(max_speed, edge["speed_kph"])
        if not max_speed:
            raise RuntimeError(f"The road graph at {path} has no drivable edges.")
        self.max_speed_mps = max_speed / 3.6
        self.node_ids = tuple(self.graph.nodes)
        self.latitudes = np.array([self.graph.nodes[node]["y"] for node in self.node_ids])
        self.longitudes = np.array([self.graph.nodes[node]["x"] for node in self.node_ids])

    def nearest_node(self, lat: float, lon: float) -> int:
        distances = ox.distance.great_circle(lat, lon, self.latitudes, self.longitudes)
        index = int(distances.argmin())
        if distances[index] > MAX_SNAP_METERS:
            raise PointOutsideGraph(f"Point is over {MAX_SNAP_METERS} m from a routable node.")
        return self.node_ids[index]

    def estimate_seconds(self, source: int, destination: int) -> float:
        start = self.graph.nodes[source]
        end = self.graph.nodes[destination]
        meters = ox.distance.great_circle(start["y"], start["x"], end["y"], end["x"])
        return float(meters) / self.max_speed_mps

    def path(self, source: int, destination: int, graph: nx.MultiDiGraph | None = None):
        graph = self.graph if graph is None else graph
        nodes = nx.astar_path(
            graph, source, destination, heuristic=self.estimate_seconds, weight="travel_time"
        )
        edges = [
            (u, v, min(graph[u][v], key=lambda key: graph[u][v][key]["travel_time"]))
            for u, v in zip(nodes, nodes[1:])
        ]
        return nodes, edges

    def edge_coordinates(self, u: int, v: int, key: int) -> list[tuple[float, float]]:
        start, end = self.graph.nodes[u], self.graph.nodes[v]
        origin = (start["x"], start["y"])
        geometry = self.graph[u][v][key].get("geometry")
        if geometry is None:
            return [origin, (end["x"], end["y"])]
        points = list(geometry.coords)
        if points[-1] == origin:
            points.reverse()
        return points

    def route(self, source: int, destination: int) -> tuple[list[int], float, float, list[list[float]]]:
        nodes, edges = self.path(source, destination)
        start = self.graph.nodes[source]
        coordinates = [[start["x"], start["y"]]]
        distance_m = travel_time_s = 0.0
        for u, v, key in edges:
            edge = self.graph[u][v][key]
            distance_m += edge["length"]
            travel_time_s += edge["travel_time"]
            coordinates.extend([lon, lat] for lon, lat in self.edge_coordinates(u, v, key)[1:])

        if len(nodes) == 1:
            coordinates.append(coordinates[0].copy())
        return nodes, distance_m, travel_time_s, coordinates
