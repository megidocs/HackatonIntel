import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import networkx as nx
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from .routing import DEFAULT_GRAPH_PATH, ManhattanRouter, PointOutsideGraph


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    path = Path(os.environ.get("CLEARPATH_GRAPH_PATH", DEFAULT_GRAPH_PATH))
    app.state.router = ManhattanRouter(path)
    yield


app = FastAPI(title="ClearPath AI", version="0.1.0", lifespan=lifespan)


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
