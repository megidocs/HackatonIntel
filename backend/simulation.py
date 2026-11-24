"""In-memory desktop traffic simulation using the milestone 1 road graph."""

from bisect import bisect_right
from collections import defaultdict, deque
from dataclasses import dataclass
from itertools import accumulate, pairwise
from math import hypot
from random import Random
from threading import Lock

import networkx as nx
from shapely import concave_hull
from shapely.geometry import MultiPoint, mapping

from .routing import ManhattanRouter

Edge = tuple[int, int, int]
Point = tuple[float, float]
SIGNAL_CYCLE = 24
GAP_METERS = 7


def feature(geometry: dict, **properties) -> dict:
    return {"type": "Feature", "geometry": geometry, "properties": properties}


def collection(features: list[dict]) -> dict:
    return {"type": "FeatureCollection", "features": features}


@dataclass(frozen=True)
class Road:
    key: Edge
    segment: int
    points: list[Point]
    offsets: list[float]
    meters: float
    seconds: float
    north_south: bool

    def position(self, meters: float) -> Point:
        if meters >= self.meters:
            return self.points[-1]
        index = bisect_right(self.offsets, meters)
        low, high = self.offsets[index - 1], self.offsets[index]
        fraction = (meters - low) / (high - low)
        a, b = self.points[index - 1], self.points[index]
        return a[0] + (b[0] - a[0]) * fraction, a[1] + (b[1] - a[1]) * fraction


@dataclass
class Vehicle:
    id: int
    road: Road
    meters: float = 0
    stopped: bool = False


class Simulation:
    def __init__(self, router: ManhattanRouter):
        self.router = router
        self.lock = Lock()
        self.roads: dict[Edge, Road] = {}
        self.outgoing: dict[int, list[Road]] = defaultdict(list)
        self.nodes = {node: (data["x"], data["y"]) for node, data in router.graph.nodes(data=True)}
        self.signals = {
            node: (node % 7) * 3
            for node, data in router.graph.nodes(data=True)
            if "traffic_signals" in str(data.get("highway", ""))
        }
        segments = {}
        street_features = []
        for u, v, key, data in router.graph.edges(keys=True, data=True):
            points = router.edge_coordinates(u, v, key)
            canonical = min(tuple(points), tuple(reversed(points)))
            segment = segments.setdefault(canonical, len(segments))
            if segment == len(street_features):
                street_features.append(feature(
                    {"type": "LineString", "coordinates": points},
                    segment=segment, name=data.get("name") or "Unnamed road",
                    kind=data.get("highway", ""),
                ))
            lengths = list(accumulate(
                (hypot((b[0] - a[0]) * .76, b[1] - a[1]) for a, b in pairwise(points)),
                initial=0.0,
            ))
            if not lengths[-1]:
                continue
            meters = data["length"]
            offsets = [length / lengths[-1] * meters for length in lengths]
            a, b = points[-2:]
            north_south = abs(b[1] - a[1]) >= .76 * abs(b[0] - a[0])
            road = Road((u, v, key), segment, points, offsets, meters, data["travel_time"], north_south)
            self.roads[road.key] = road
            self.outgoing[u].append(road)

        self.street_features = street_features
        land = concave_hull(MultiPoint(list(self.nodes.values())), ratio=.06).buffer(.00045)
        self.map_data = {
            "roads": collection(street_features),
            "signals": collection([
                feature({"type": "Point", "coordinates": self.nodes[node]}, offset=offset)
                for node, offset in self.signals.items()
            ]),
            "land": collection([feature(mapping(land))]),
        }
        self.default_origin = router.nearest_node(40.7391, -73.9760)
        self.default_destination = router.nearest_node(40.7580, -73.9855)
        self.reset()

    def reset(self) -> None:
        self.random = Random(40)
        self.time = 0.0
        self.running = False
        self.speed = 4
        self.closed: set[int] = set()
        self.origin, self.destination = self.default_origin, self.default_destination
        self.emergency: Vehicle | None = None
        self.traffic: list[Vehicle] = []
        self.set_density(240)
        self.plan_route(keep_vehicle=False)

    def set_density(self, density: int) -> None:
        if density <= len(self.traffic):
            self.traffic = self.traffic[:density]
            return
        roads = [road for road in self.roads.values() if road.segment not in self.closed]
        if not roads:
            return
        for id in range(len(self.traffic) + 1, density + 1):
            road = self.random.choice(roads)
            self.traffic.append(Vehicle(id, road, self.random.random() * road.meters * .7))

    def set_point(self, mode: str, node: int) -> None:
        if mode == "origin":
            self.origin = node
        else:
            self.destination = node
        self.plan_route(keep_vehicle=False)

    def toggle_closure(self, segment: int) -> None:
        if segment in self.closed:
            self.closed.remove(segment)
        else:
            self.closed.add(segment)
        self.plan_route(keep_vehicle=True)

    def plan_route(self, keep_vehicle: bool) -> None:
        active = self.emergency if keep_vehicle and self.emergency and self.emergency.meters > 0 else None
        source = active.road.key[1] if active else self.origin
        graph = nx.subgraph_view(
            self.router.graph,
            filter_edge=lambda u, v, key: (
                (u, v, key) in self.roads and self.roads[u, v, key].segment not in self.closed
            ),
        )
        try:
            _, keys = self.router.path(source, self.destination, graph)
        except nx.NetworkXNoPath:
            keys = []
            self.route_status = "blocked"
        else:
            self.route_status = "en_route" if keys or (active and active.meters < active.road.meters) else "arrived"

        self.pending = deque(self.roads[key] for key in keys)
        roads = ([active.road] if active else []) + list(self.pending)
        self.route_line = [self.nodes[roads[0].key[0]]] if roads else []
        self.route_meters = sum(road.meters for road in roads) - (active.meters if active else 0)
        self.route_seconds = sum(road.seconds for road in roads)
        if active:
            self.route_seconds -= active.road.seconds * active.meters / active.road.meters
        for road in roads:
            self.route_line.extend(road.points[1:])
        self.emergency = active
        if not active and self.pending:
            self.emergency = Vehicle(0, self.pending.popleft())

    def advance(self, elapsed: float) -> None:
        with self.lock:
            if not self.running:
                return
            dt = min(elapsed, .2) * self.speed
            self.time += dt
            groups: dict[Edge, list[Vehicle]] = defaultdict(list)
            for traffic in self.traffic:
                groups[traffic.road.key].append(traffic)
            if self.emergency and self.route_status != "arrived":
                groups[self.emergency.road.key].append(self.emergency)

            # Process leaders first and limit movement behind them on each directed road.
            occupied = {key: min(car.meters for car in cars) for key, cars in groups.items()}
            for cars in groups.values():
                limit = float("inf")
                for car in sorted(cars, key=lambda car: car.meters, reverse=True):
                    road = car.road
                    old = car.meters
                    speed = road.meters / road.seconds * (.75 if car.id else 1)
                    target = min(road.meters, old + speed * dt, limit)
                    offset = self.signals.get(road.key[1])
                    green = True
                    if offset is not None:
                        phase = (self.time + offset) % SIGNAL_CYCLE
                        green = phase < 10 if road.north_south else 12 <= phase < 22
                        if not green:
                            target = min(target, max(0, road.meters - 2))
                    car.meters = max(old, target)
                    car.stopped = car.meters - old < .03
                    limit = car.meters - GAP_METERS
                    if green and car.meters >= road.meters:
                        self.enter_next(car, occupied)

    def enter_next(self, car: Vehicle, occupied: dict[Edge, float]) -> None:
        u, v, _ = car.road.key
        if car.id == 0:
            if not self.pending:
                if self.route_status == "en_route":
                    self.route_status = "arrived"
                return
            next_road = self.pending[0]
        else:
            options = [road for road in self.outgoing[v] if road.segment not in self.closed]
            if not options:
                return
            forward = [road for road in options if road.key[1] != u]
            next_road = self.random.choice(forward or options)
        if occupied.get(next_road.key, float("inf")) < GAP_METERS:
            return
        if car.id == 0:
            self.pending.popleft()
        car.road, car.meters = next_road, 0
        occupied[next_road.key] = 0

    def snapshot(self) -> dict:
        vehicles = [*self.traffic, self.emergency] if self.emergency else self.traffic
        return {
            "time": round(self.time, 2),
            "running": self.running,
            "speed": self.speed,
            "density": len(self.traffic),
            "vehicles": [
                {"id": car.id, "point": car.road.position(car.meters), "stopped": car.stopped}
                for car in vehicles
            ],
            "signal_count": len(self.signals),
            "closures": sorted(self.closed),
            "default_origin": self.nodes[self.default_origin],
            "default_destination": self.nodes[self.default_destination],
            "origin": self.nodes[self.origin],
            "destination": self.nodes[self.destination],
            "route": self.route_line,
            "route_status": self.route_status,
            "route_meters": round(self.route_meters),
            "route_seconds": round(self.route_seconds),
        }
