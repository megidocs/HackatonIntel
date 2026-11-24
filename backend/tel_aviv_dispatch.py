"""Dispatch rehearsal for a simulated Tel Aviv fleet."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

import networkx as nx
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .routing import ManhattanRouter
from .scenarios import TEL_AVIV, Place
from .simulation import Simulation

UnitType = Literal["medical", "fire", "police"]


@dataclass(frozen=True)
class DemoUnit:
    id: str
    name: str
    kind: UnitType
    base: Place


FLEET = (
    DemoUnit("ambulance-1", "Ambulance 1", "medical", Place("Pinkas", 34.786581, 32.090975, "פנקס")),
    DemoUnit("fire-1", "Fire engine 1", "fire", Place("Jabotinsky", 34.778341, 32.088846, "ז׳בוטינסקי")),
    DemoUnit("police-1", "Police car 1", "police", Place("Ben Yehuda", 34.768102, 32.076202, "בן יהודה")),
    DemoUnit("ambulance-2", "Ambulance 2", "medical", Place("Nahmani", 34.776902, 32.065372, "נחמני")),
    DemoUnit("fire-2", "Fire engine 2", "fire", Place("Jaffa Road", 34.771447, 32.060684, "דרך יפו")),
    DemoUnit("police-2", "Police car 2", "police", Place("Sportek", 34.783924, 32.098597, "ספורטק")),
)


class DemoReport(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    report: str = Field(min_length=1, max_length=1200)
    location: str = Field(min_length=1, max_length=80)
    unit_type: UnitType


class DemoApproval(DemoReport):
    unit_id: str = Field(min_length=1, max_length=20)
    version: int = Field(ge=0)


class TelAvivDispatch(Simulation):
    def __init__(self, router: ManhattanRouter):
        self.dispatch_version = 0
        super().__init__(router, dispatch_mode=True, scenario=TEL_AVIV)
        self.bases = {unit.id: router.nearest_node(unit.base.lat, unit.base.lon) for unit in FLEET}
        places = (*TEL_AVIV.incidents, TEL_AVIV.origin, *(unit.base for unit in FLEET))
        self.destinations = {
            place.name: router.nearest_node(place.lat, place.lon) for place in places
        }
        self.map_data["report_locations"] = [{"name": place.name, "hebrew": place.hebrew} for place in places]

    def reset(self):
        super().reset()
        self.dispatched_unit: str | None = None
        self.dispatch_version += 1

    def unit_busy(self, unit_id: str) -> bool:
        return unit_id == self.dispatched_unit and self.route_status in {"en_route", "blocked"}

    def snapshot(self) -> dict:
        result = super().snapshot()
        result["fleet"] = [
            {
                "id": unit.id, "name": unit.name, "type": unit.kind,
                "base": unit.base.name, "hebrew": unit.base.hebrew, "point": self.nodes[self.bases[unit.id]],
                "available": not self.unit_busy(unit.id),
            }
            for unit in FLEET
        ]
        result["dispatched_unit"] = self.dispatched_unit
        result["dispatch_version"] = self.dispatch_version
        return result

    def candidates(self, report: DemoReport) -> list[dict]:
        destination = self.destinations.get(report.location)
        if destination is None:
            raise HTTPException(422, "Choose a location from the Tel Aviv map.")
        graph = self.open_graph()
        candidates = []
        for unit in FLEET:
            if unit.kind != report.unit_type or self.unit_busy(unit.id):
                continue
            try:
                _, edges = self.router.path(self.bases[unit.id], destination, graph)
            except nx.NetworkXNoPath:
                continue
            seconds = round(sum(self.roads[edge].seconds for edge in edges))
            candidates.append({"id": unit.id, "name": unit.name, "base": unit.base.name, "eta_seconds": seconds})
        return sorted(candidates, key=lambda unit: (unit["eta_seconds"], unit["id"]))

    def approve(self, report: DemoApproval) -> dict:
        if report.version != self.dispatch_version:
            raise HTTPException(409, "The simulation changed. Review your report again.")
        if self.dispatched_unit and self.unit_busy(self.dispatched_unit):
            raise HTTPException(409, "Wait for the current vehicle to arrive before approving another trip.")
        if not any(unit["id"] == report.unit_id for unit in self.candidates(report)):
            raise HTTPException(409, "That vehicle is no longer available for this route. Review the report again.")
        self.launch_dispatch(
            (datetime.now(UTC), str(uuid4())), self.bases[report.unit_id],
            self.destinations[report.location], report.location,
        )
        self.dispatched_unit = report.unit_id
        self.dispatch_version += 1
        self.running = True
        return self.snapshot()
