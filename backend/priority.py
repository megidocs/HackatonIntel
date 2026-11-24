"""Emergency approach priority and alerts for the in-memory simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .simulation import Edge, Point, Road, Vehicle

LOOKAHEAD_SECONDS = 20
CORRIDOR_METERS = 400
CLEARANCE_SECONDS = 2


@dataclass(frozen=True)
class SignalOverride:
    approach: bool | None
    ready_at: float


class PriorityCorridor:
    def __init__(self):
        self.enabled = True
        self.signals: dict[int, SignalOverride] = {}
        self.alerted: set[int] = set()
        self.line: list[Point] = []

    def update(
        self,
        now: float,
        vehicle: Vehicle | None,
        pending: list[Road],
        signal_nodes: dict[int, int],
        traffic: list[Vehicle],
    ) -> None:
        requests: dict[int, bool] = {}
        ranges: dict[Edge, tuple[float, float]] = {}
        self.line = []
        if self.enabled and vehicle:
            self.line.append(vehicle.road.position(vehicle.meters))
            eta, distance = 0.0, 0.0
            for index, road in enumerate([vehicle.road, *pending]):
                start = vehicle.meters if index == 0 else 0.0
                remaining = road.meters - start
                eta += remaining / road.meters * road.seconds
                _, signal, _ = road.key
                if signal in signal_nodes and eta <= LOOKAHEAD_SECONDS:
                    requests.setdefault(signal, road.north_south)
                if distance < CORRIDOR_METERS and remaining > 0:
                    end = min(road.meters, start + CORRIDOR_METERS - distance)
                    ranges.setdefault(road.key, (start, end))
                    self.line.extend(point for offset, point in zip(road.offsets, road.points) if start < offset < end)
                    self.line.append(road.position(end))
                distance += remaining
                if distance >= CORRIDOR_METERS and eta > LOOKAHEAD_SECONDS:
                    break

        for node, override in list(self.signals.items()):
            if node not in requests:
                if override.approach is not None:
                    self.signals[node] = SignalOverride(None, now + CLEARANCE_SECONDS)
                elif now >= override.ready_at:
                    del self.signals[node]
        for node, approach in requests.items():
            current = self.signals.get(node)
            if current is None or current.approach != approach:
                self.signals[node] = SignalOverride(approach, now + CLEARANCE_SECONDS)

        self.alerted = {
            car.id
            for car in traffic
            if (bounds := ranges.get(car.road.key)) and bounds[0] <= car.meters <= bounds[1]
        }

    def can_enter(self, now: float, node: int, north_south: bool) -> bool | None:
        override = self.signals.get(node)
        if override is None:
            return None
        return now >= override.ready_at and override.approach == north_south
