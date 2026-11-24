import asyncio
import os
from contextlib import asynccontextmanager, suppress
from hmac import compare_digest
from pathlib import Path
from time import monotonic
from typing import Literal

import networkx as nx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .dispatch import DispatchServices, router as dispatch_router
from .mobile import mobile_router
from .routing import DEFAULT_GRAPH_PATH, ManhattanRouter, PointOutsideGraph
from .scenarios import TEL_AVIV, TEL_AVIV_BUNDLE
from .simulation import Simulation
from .tel_aviv_dispatch import DemoApproval, DemoReport, TelAvivDispatch

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
    priority: bool | None = None
    reset: bool = False


class SimulationPoint(Position):
    target: Literal["origin", "destination"]


async def advance_simulations(simulations: tuple[Simulation, ...]):
    previous = monotonic()
    while True:
        await asyncio.sleep(.1)
        current = monotonic()
        for simulation in simulations:
            simulation.advance(current - previous)
        previous = current


@asynccontextmanager
async def lifespan(app: FastAPI):
    path = Path(os.environ.get("CLEARPATH_GRAPH_PATH", DEFAULT_GRAPH_PATH))
    app.state.router = ManhattanRouter(path)
    app.state.simulation = Simulation(
        app.state.router, dispatch_mode=os.environ.get("CLEARPATH_DISPATCH_SIMULATION") == "1",
    )
    tel_aviv_path = Path(os.environ.get("CLEARPATH_TEL_AVIV_GRAPH_PATH", TEL_AVIV_BUNDLE))
    tel_aviv_router = ManhattanRouter(tel_aviv_path)
    app.state.tel_aviv_dispatch = TelAvivDispatch(tel_aviv_router)
    app.state.simulations = {
        "manhattan": app.state.simulation,
        "tel-aviv": Simulation(tel_aviv_router, scenario=TEL_AVIV),
        "tel-aviv-dispatch": app.state.tel_aviv_dispatch,
    }
    app.state.dispatch = DispatchServices.from_environment()
    if app.state.dispatch is not None:
        app.state.simulations["tel-aviv-reports"] = Simulation(tel_aviv_router, dispatch_mode=True, scenario=TEL_AVIV)
    app.state.simulation_maps = {
        city: JSONResponse(simulation.map_data).body
        for city, simulation in app.state.simulations.items()
    }
    app.state.control_token = os.environ.get("CLEARPATH_CONTROL_TOKEN", "")
    app.state.restricted_controls = (
        bool(app.state.control_token)
        or os.environ.get("CLEARPATH_PUBLIC_DEMO") == "1"
        or os.environ.get("RENDER") == "true"
    )
    timer = asyncio.create_task(advance_simulations(tuple(app.state.simulations.values())))
    try:
        yield
    finally:
        timer.cancel()
        with suppress(asyncio.CancelledError):
            await timer
        if app.state.dispatch:
            app.state.dispatch.close()


app = FastAPI(title="ClearPath AI", version="0.1.0", lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=700, compresslevel=3)
app.include_router(mobile_router)
app.include_router(dispatch_router)
app.mount("/sim/assets", StaticFiles(directory=FRONTEND / "public"), name="simulation-assets")


@app.get("/health")
def health(request: Request):
    graph = request.app.state.router.graph
    result = {"status": "ok", "nodes": len(graph), "directed_edges": graph.number_of_edges()}
    commit = os.environ.get("RENDER_GIT_COMMIT") or os.environ.get("CLEARPATH_RELEASE")
    if commit:
        result["release"] = commit
    return result


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


@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse("/simulator")


@app.get("/simulator", include_in_schema=False)
@app.get("/simulator/tel-aviv", include_in_schema=False)
@app.get("/simulator/tel-aviv/dispatch", include_in_schema=False)
def simulator_page():
    return FileResponse(FRONTEND / "public" / "index.html")


@app.get("/simulator/tel-aviv/reports", include_in_schema=False)
def report_simulator_page(request: Request):
    if request.app.state.dispatch is None:
        raise HTTPException(status_code=404)
    return simulator_page()


@app.get("/dispatch/reports", include_in_schema=False)
def report_page(request: Request):
    if request.app.state.dispatch is None:
        raise HTTPException(status_code=404)
    return FileResponse(FRONTEND / "public" / "dispatch-report.html", headers={"Cache-Control": "no-store"})


@app.get("/sim/vendor/{filename}", include_in_schema=False)
def maplibre_file(filename: str):
    if filename not in MAPLIBRE_FILES:
        raise HTTPException(status_code=404)
    path = FRONTEND / "node_modules" / "maplibre-gl" / "dist" / filename
    if not path.is_file():
        raise HTTPException(status_code=503, detail="Install simulator assets with npm ci --prefix frontend.")
    media_type = "text/css" if filename.endswith(".css") else "text/javascript"
    return FileResponse(path, media_type=media_type)


def simulation_city(request: Request) -> str:
    city = request.path_params.get("city", "manhattan")
    if city not in request.app.state.simulations:
        raise HTTPException(status_code=404, detail="Simulator city not found.")
    return city


@app.get("/simulation/map")
@app.get("/simulation/{city}/map", include_in_schema=False)
def simulation_map(request: Request):
    return Response(
        request.app.state.simulation_maps[simulation_city(request)], media_type="application/json",
    )


@app.get("/simulation/state")
@app.get("/simulation/{city}/state", include_in_schema=False)
def simulation_state(request: Request):
    simulation = request.app.state.simulations[simulation_city(request)]
    with simulation.lock:
        return simulation.snapshot()


def control_allowed(request: Request) -> bool:
    if not request.app.state.restricted_controls:
        return True
    expected = request.app.state.control_token
    supplied = request.headers.get("X-ClearPath-Control-Token", "")
    return bool(expected) and compare_digest(expected.encode(), supplied.encode())


def require_control(request: Request) -> None:
    if not control_allowed(request):
        raise HTTPException(status_code=403, detail="Presenter access is required.")


@app.get("/simulation/access", include_in_schema=False)
def simulation_access(request: Request):
    return JSONResponse(
        {"restricted": request.app.state.restricted_controls, "allowed": control_allowed(request)},
        headers={"Cache-Control": "no-store"},
    )


@app.post("/simulation/tel-aviv-dispatch/propose", include_in_schema=False)
def propose_tel_aviv_dispatch(payload: DemoReport, request: Request):
    require_control(request)
    simulation = request.app.state.tel_aviv_dispatch
    with simulation.lock:
        return {"version": simulation.dispatch_version, "candidates": simulation.candidates(payload)}


@app.post("/simulation/tel-aviv-dispatch/approve", include_in_schema=False)
def approve_tel_aviv_dispatch(payload: DemoApproval, request: Request):
    require_control(request)
    simulation = request.app.state.tel_aviv_dispatch
    with simulation.lock:
        return simulation.approve(payload)


@app.post("/simulation/control")
@app.post("/simulation/{city}/control", include_in_schema=False)
def simulation_control(payload: SimulationControl, request: Request):
    require_control(request)
    simulation = request.app.state.simulations[simulation_city(request)]
    with simulation.lock:
        if payload.reset:
            simulation.reset()
        if payload.running is not None:
            simulation.running = payload.running
        if payload.speed is not None:
            simulation.speed = payload.speed
        if payload.density is not None:
            simulation.set_density(payload.density)
            simulation.update_priority()
        if payload.priority is not None:
            simulation.set_priority(payload.priority)
        return simulation.snapshot()


@app.post("/simulation/closure/{segment}")
@app.post("/simulation/{city}/closure/{segment}", include_in_schema=False)
def simulation_closure(segment: int, request: Request):
    require_control(request)
    simulation = request.app.state.simulations[simulation_city(request)]
    if not 0 <= segment < len(simulation.street_features):
        raise HTTPException(status_code=404, detail="Road segment not found.")
    with simulation.lock:
        simulation.toggle_closure(segment)
        return simulation.snapshot()


@app.post("/simulation/point")
@app.post("/simulation/{city}/point", include_in_schema=False)
def simulation_point(payload: SimulationPoint, request: Request):
    require_control(request)
    simulation = request.app.state.simulations[simulation_city(request)]
    if simulation.dispatch_mode:
        raise HTTPException(status_code=409, detail="An approved dispatch sets the route in this demo.")
    try:
        node = simulation.router.nearest_node(payload.lat, payload.lon)
    except PointOutsideGraph as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    with simulation.lock:
        simulation.set_point(payload.target, node)
        return simulation.snapshot()
