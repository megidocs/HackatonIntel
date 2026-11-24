import asyncio
import os
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from time import monotonic
from typing import Literal

import networkx as nx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .routing import DEFAULT_GRAPH_PATH, ManhattanRouter, PointOutsideGraph
from .simulation import Simulation

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
MAPLIBRE_FILES = {
    "maplibre-gl.mjs", "maplibre-gl-shared.mjs", "maplibre-gl-worker.mjs", "maplibre-gl.css"
}


class Position(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class RouteRequest(BaseModel):
    origin: Position
    destination: Position


class LineString(BaseModel):
    type: Literal["LineString"] = "LineString"
    coordinates: list[list[float]]


class RouteResponse(BaseModel):
    nodes: list[int]
    distance_m: float
    travel_time_s: float
    geometry: LineString


class SimulationControl(BaseModel):
    running: bool | None = None
    speed: Literal[1, 4, 8] | None = None
    density: int | None = Field(default=None, ge=0, le=500)
    reset: bool = False


class SimulationPoint(Position):
    target: Literal["origin", "destination"]


async def advance_simulation(simulation: Simulation):
    previous = monotonic()
    while True:
        await asyncio.sleep(.1)
        current = monotonic()
        simulation.advance(current - previous)
        previous = current


@asynccontextmanager
async def lifespan(app: FastAPI):
    path = Path(os.environ.get("CLEARPATH_GRAPH_PATH", DEFAULT_GRAPH_PATH))
    app.state.router = ManhattanRouter(path)
    app.state.simulation = Simulation(app.state.router)
    app.state.simulation_map = JSONResponse(app.state.simulation.map_data)
    timer = asyncio.create_task(advance_simulation(app.state.simulation))
    try:
        yield
    finally:
        timer.cancel()
        with suppress(asyncio.CancelledError):
            await timer


app = FastAPI(title="ClearPath AI", version="0.1.0", lifespan=lifespan)
app.mount("/sim/assets", StaticFiles(directory=FRONTEND / "public"), name="simulation-assets")


@app.get("/health")
def health(request: Request):
    graph = request.app.state.router.graph
    return {"status": "ok", "nodes": len(graph), "directed_edges": graph.number_of_edges()}


@app.post("/route", response_model=RouteResponse)
def route(payload: RouteRequest, request: Request) -> RouteResponse:
    router = request.app.state.router
    try:
        source = router.nearest_node(payload.origin.lat, payload.origin.lon)
        destination = router.nearest_node(payload.destination.lat, payload.destination.lon)
        nodes, distance_m, travel_time_s, coordinates = router.route(source, destination)
    except PointOutsideGraph as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except nx.NetworkXNoPath as error:
        raise HTTPException(status_code=404, detail="No driving route between the snapped nodes.") from error
    return RouteResponse(
        nodes=nodes,
        distance_m=round(distance_m, 2),
        travel_time_s=round(travel_time_s, 2),
        geometry=LineString(coordinates=coordinates),
    )


@app.get("/simulator", include_in_schema=False)
def simulator_page():
    return FileResponse(FRONTEND / "public" / "index.html")


@app.get("/sim/vendor/{filename}", include_in_schema=False)
def maplibre_file(filename: str):
    if filename not in MAPLIBRE_FILES:
        raise HTTPException(status_code=404)
    path = FRONTEND / "node_modules" / "maplibre-gl" / "dist" / filename
    if not path.is_file():
        raise HTTPException(status_code=503, detail="Install simulator assets with npm ci --prefix frontend.")
    media_type = "text/css" if filename.endswith(".css") else "text/javascript"
    return FileResponse(path, media_type=media_type)


@app.get("/simulation/map")
def simulation_map(request: Request):
    return request.app.state.simulation_map


@app.get("/simulation/state")
def simulation_state(request: Request):
    simulation = request.app.state.simulation
    with simulation.lock:
        return simulation.snapshot()


@app.post("/simulation/control")
def simulation_control(payload: SimulationControl, request: Request):
    simulation = request.app.state.simulation
    with simulation.lock:
        if payload.reset:
            simulation.reset()
        if payload.running is not None:
            simulation.running = payload.running
        if payload.speed is not None:
            simulation.speed = payload.speed
        if payload.density is not None:
            simulation.set_density(payload.density)
        return simulation.snapshot()


@app.post("/simulation/closure/{segment}")
def simulation_closure(segment: int, request: Request):
    simulation = request.app.state.simulation
    if not 0 <= segment < len(simulation.street_features):
        raise HTTPException(status_code=404, detail="Road segment not found.")
    with simulation.lock:
        simulation.toggle_closure(segment)
        return simulation.snapshot()


@app.post("/simulation/point")
def simulation_point(payload: SimulationPoint, request: Request):
    simulation = request.app.state.simulation
    try:
        node = simulation.router.nearest_node(payload.lat, payload.lon)
    except PointOutsideGraph as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    with simulation.lock:
        simulation.set_point(payload.target, node)
        return simulation.snapshot()
