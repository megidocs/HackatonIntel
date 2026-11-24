"""Bounded read-only planning for the dispatch review workflow."""

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from math import cos, hypot, radians
from time import perf_counter
from typing import Callable
from uuid import UUID

import httpx
import networkx as nx
from pydantic import BaseModel, ConfigDict, TypeAdapter

from .report_extraction import LOCATIONS, ReportDraft, UnitKind, extract_report, verified_location
from .routing import ManhattanRouter, PointOutsideGraph

TOOL_LIMIT = 8
DEFAULT_STATIONS = {"medical": "Bellevue Hospital", "fire": "Union Square", "police": "Times Square"}
TOOL_HELP = {
    "geocode": "Resolve the reported place against the local Manhattan catalog.",
    "get_recent_incidents": "Check for a matching open incident near the destination.",
    "find_available_units": "Find available units of the required types.",
    "get_eta": "Route the available units to the destination.",
    "draft_dispatch": "Return the reviewed candidates as a pending draft.",
    "ask_dispatcher": "Stop and ask the dispatcher for missing or conflicting information.",
}


class BoardUnit(BaseModel):
    model_config = ConfigDict(extra="ignore")
    unit_id: UUID
    unit_type: UnitKind
    dispatch_id: UUID | None
    station: str | None = None


@dataclass
class PlannerBudget:
    deadline: float
    trace: list[dict]
    model_calls: int = 0
    usage: dict = field(default_factory=dict)

    def remaining(self) -> float:
        seconds = self.deadline - perf_counter()
        if seconds <= 0:
            raise TimeoutError("Planning timed out.")
        return seconds

    def add(self, tool: str, parameters: dict, observation):
        self.remaining()
        if len(self.trace) >= TOOL_LIMIT:
            raise TimeoutError("Tool limit reached.")
        self.trace.append({"tool": tool, "parameters": parameters, "result": observation})


def choose_tool(client: httpx.Client, base_url: str, options: list[str], facts: dict, budget: PlannerBudget) -> str:
    if len(options) == 1:
        return options[0]
    budget.model_calls += 1
    response = client.post(
        base_url.rstrip("/") + "/v1/chat/completions",
        timeout=budget.remaining(),
        json={
            "temperature": 0,
            "max_tokens": 45,
            "chat_template_kwargs": {"enable_thinking": False},
            "messages": [{
                "role": "system",
                "content": "Choose one allowed dispatcher planning tool from the typed facts. "
                           "Check a possible duplicate before spending work on routing. Return JSON only.",
            }, {
                "role": "user",
                "content": json.dumps({"facts": facts, "tools": {name: TOOL_HELP[name] for name in options}}),
            }],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "tool_choice", "strict": True, "schema": {
                    "type": "object", "additionalProperties": False, "required": ["tool"],
                    "properties": {"tool": {"type": "string", "enum": options}},
                }},
            },
        },
    )
    response.raise_for_status()
    payload = response.json()
    for key in ("prompt_tokens", "completion_tokens"):
        budget.usage[key] = budget.usage.get(key, 0) + payload.get("usage", {}).get(key, 0)
    content = json.loads(payload["choices"][0]["message"]["content"])
    tool = content.get("tool") if isinstance(content, dict) and set(content) == {"tool"} else None
    if tool not in options:
        raise ValueError("The model selected an unavailable tool.")
    return tool


def required_units(draft: ReportDraft, report: str) -> list[str]:
    """Apply minimum coverage for an incident and obvious compound hazards."""
    minimum = {"medical": "medical", "fire": "fire", "roadblock": "police", "accident": "medical"}
    units = [minimum[draft.incident_type], *draft.required_units]
    text = report.casefold()
    if draft.incident_type == "accident" and any(term in text for term in ("trapped", "pinned", "cannot get out")):
        units.extend(("medical", "fire"))
    return sorted(set(units))


def distance_m(alat, alon, blat, blon):
    north = (alat - blat) * 111_195
    east = (alon - blon) * 111_195 * cos(radians((alat + blat) / 2))
    return hypot(north, east)


def available_units(board: dict, kinds: list[str], destination: dict) -> list[dict]:
    units = []
    for unit in TypeAdapter(list[BoardUnit]).validate_python(board["units"]):
        if unit.dispatch_id is not None or unit.unit_type not in kinds:
            continue
        station = unit.station or DEFAULT_STATIONS[unit.unit_type]
        if station not in LOCATIONS:
            continue
        lat, lon, _ = LOCATIONS[station]
        if distance_m(lat, lon, destination["lat"], destination["lon"]) <= 8000:
            units.append({"unit_id": str(unit.unit_id), "unit_type": unit.unit_type, "station": station})
    # Limit work and retain a deterministic ordering for the current depot model.
    return [unit for kind in kinds for unit in [row for row in units if row["unit_type"] == kind][:4]]


def unit_etas(router: ManhattanRouter, destination: dict, units: list[dict], blocked: frozenset) -> list[dict]:
    graph = nx.subgraph_view(router.graph, filter_edge=lambda u, v, key: (u, v, key) not in blocked)

    def eta(unit):
        lat, lon, _ = LOCATIONS[unit["station"]]
        try:
            source = router.nearest_node(lat, lon)
            _, edges = router.path(source, destination["osm_node_id"], graph=graph)
        except (nx.NetworkXNoPath, PointOutsideGraph):
            return None
        seconds = sum(graph[u][v][key]["travel_time"] for u, v, key in edges)
        return {**unit, "eta_seconds": round(seconds, 1)}

    with ThreadPoolExecutor(max_workers=min(4, len(units) or 1)) as pool:
        choices = [unit for unit in pool.map(eta, units) if unit is not None]
    return sorted(choices, key=lambda unit: (unit["eta_seconds"], unit["unit_id"]))


def plan_dispatch(
    report: str, client: httpx.Client, model_url: str, router: ManhattanRouter,
    board_loader: Callable[[], dict], blocked: frozenset = frozenset(), deadline_seconds: float = 10,
) -> dict:
    started = perf_counter()
    budget = PlannerBudget(started + deadline_seconds, [])
    location = board = available = candidates = recent = None

    def result(status, **payload):
        return {"status": status, **payload, "trace": budget.trace, "model_calls": budget.model_calls,
                "model_tokens": budget.usage,
                "elapsed_ms": round((perf_counter() - started) * 1000, 1)}

    def clarify(question):
        budget.add("ask_dispatcher", {"question": question}, "waiting_for_dispatcher")
        return result("needs_clarification", question=question)

    try:
        budget.model_calls += 1
        draft = extract_report(client, model_url, report, timeout=budget.remaining(), usage=budget.usage)
        if draft.incident_type is None or draft.severity is None:
            return clarify("What is the primary incident and how serious is it?")
        kinds = required_units(draft, report)
        incident_kind = {"medical": "medical", "fire": "fire", "accident": "medical", "roadblock": "police"}[
            draft.incident_type
        ]
        for _ in range(TOOL_LIMIT):
            budget.remaining()
            if location is None:
                options = ["geocode"]
            else:
                options = []
                if recent is None:
                    options.append("get_recent_incidents")
                if available is None:
                    options.append("find_available_units")
                elif candidates is None:
                    options.append("get_eta")
                if not options:
                    options.append("draft_dispatch")
            tool = choose_tool(client, model_url, options, {"incident": incident_kind, "unit_types": kinds}, budget)

            if tool == "geocode":
                location = verified_location(report, draft, router)
                budget.add(tool, {"location_phrase": draft.location_phrase}, location)
                if location is None:
                    return clarify("Which single supported Manhattan location should this report use?")
                if board is None:
                    board = board_loader()
            elif tool == "get_recent_incidents":
                recent = [
                    incident["incident_id"] for incident in board["incidents"]
                    if incident["incident_type"] == incident_kind and distance_m(
                        incident["latitude"], incident["longitude"], location["lat"], location["lon"]
                    ) <= 200
                ]
                budget.add(tool, {"location": location["label"], "radius_m": 200, "incident_type": incident_kind}, recent)
                if recent:
                    return clarify("A similar incident is already open nearby. Is this a separate event?")
            elif tool == "find_available_units":
                available = available_units(board, kinds, location)
                budget.add(tool, {"unit_types": kinds, "location": location["label"], "radius_m": 8000}, available)
            elif tool == "get_eta":
                candidates = unit_etas(router, location, available, blocked)
                budget.add(tool, {"unit_ids": [unit["unit_id"] for unit in available],
                                  "destination_osm_node_id": location["osm_node_id"]}, candidates)
            elif tool == "draft_dispatch":
                best = [next((unit for unit in candidates if unit["unit_type"] == kind), None) for kind in kinds]
                missing = [kind for kind, unit in zip(kinds, best) if unit is None]
                if missing:
                    return clarify(f"No reachable available unit for {', '.join(missing)}. Review manually.")
                recommended_ids = [unit["unit_id"] for unit in best]
                alternatives = [unit["unit_id"] for unit in candidates if unit["unit_id"] not in recommended_ids][:2]
                proposal = {
                    "incident": {"incident_type": incident_kind, "severity": draft.severity,
                                 "lat": location["lat"], "lon": location["lon"], "location_label": location["label"]},
                    "observed_incident_type": draft.incident_type,
                    "requested_unit_types": kinds,
                    "recommended_unit_ids": recommended_ids,
                    "alternative_unit_ids": alternatives,
                    "candidates": candidates,
                    "rationale": "Shortest available modeled ETA for each required unit type.",
                }
                budget.add(tool, {"unit_ids": recommended_ids}, {"alternatives": alternatives})
                return result("pending", proposal=proposal)
        return result("manual", reason="The planning tool limit was reached.")
    except (TimeoutError, httpx.TimeoutException):
        return result("manual", reason="The planning time limit was reached.")
    except (httpx.HTTPError, ValueError, KeyError, IndexError, PointOutsideGraph):
        return result("manual", reason="A planning input or model response could not be verified.")
