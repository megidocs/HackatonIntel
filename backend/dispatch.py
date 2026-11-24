import os
from dataclasses import dataclass
from datetime import datetime
from time import time_ns
from typing import Annotated, Literal
from urllib.parse import urlsplit
from uuid import UUID, uuid4

import httpx
import psycopg
from fastapi import APIRouter, Depends, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from psycopg.conninfo import conninfo_to_dict
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool, PoolClosed, PoolTimeout
from pydantic import BaseModel, Field
from redis import Redis, RedisError

from .copilot import DEFAULT_STATIONS, plan_dispatch
from .report_extraction import LOCATIONS, extract_report, verified_location
from .routing import PointOutsideGraph

router = APIRouter(prefix="/dispatch", tags=["Dispatch"])
bearer = HTTPBearer(auto_error=False)
Role = Literal["dispatcher", "rescue", "citizen"]

# Keep the nonce, latest sample and per-actor validation in one Redis operation.
SAVE_POSITION = """
if redis.call('EXISTS', KEYS[1]) == 1 then return 'replay' end
local prior = redis.call('GET', KEYS[2])
if prior then
    local before = cjson.decode(prior)
    local seconds = (tonumber(ARGV[1]) - before.time_ms) / 1000
    if seconds <= 0 then return 'replay' end
    local dy = (tonumber(ARGV[2]) - before.lat) * 111195
    local dx = (tonumber(ARGV[3]) - before.lon) * 111195 *
        math.cos(math.rad((tonumber(ARGV[2]) + before.lat) / 2))
    if math.sqrt(dx * dx + dy * dy) > 15 + 60 * seconds then return 'speed' end
end
redis.call('SET', KEYS[1], '1', 'EX', 60)
redis.call('SET', KEYS[2], ARGV[4], 'EX', 60)
return 'accepted'
"""


@dataclass(frozen=True)
class Actor:
    user_id: UUID
    role: Role


@dataclass
class DispatchServices:
    database: ConnectionPool
    identity: httpx.Client
    redis: Redis

    @classmethod
    def from_environment(cls):
        dsn = os.getenv("CLEARPATH_DATABASE_URL")
        redis_url = os.getenv("CLEARPATH_REDIS_URL")
        project = os.getenv("CLEARPATH_SUPABASE_URL")
        publishable = os.getenv("CLEARPATH_SUPABASE_PUBLISHABLE_KEY")
        settings = (dsn, redis_url, project, publishable)
        if not any(settings):
            return None
        if not all(settings):
            raise RuntimeError("Set all four ClearPath dispatch configuration variables.")
        database = conninfo_to_dict(dsn)
        if database.get("host") not in {"localhost", "127.0.0.1", "::1"} and database.get("sslmode") != "verify-full":
            raise RuntimeError("A remote ClearPath database requires sslmode=verify-full.")
        endpoint = urlsplit(project)
        if endpoint.scheme != "https" or not endpoint.hostname or endpoint.username or endpoint.query or endpoint.fragment:
            raise RuntimeError("Use the HTTPS Supabase project base URL.")
        return cls(
            ConnectionPool(
                dsn, min_size=0, max_size=4, open=True, timeout=5,
                kwargs={"connect_timeout": 4, "options": "-c statement_timeout=5000 -c lock_timeout=3000"},
            ),
            httpx.Client(base_url=project.rstrip("/") + "/", headers={"apikey": publishable}, timeout=5),
            Redis.from_url(redis_url, decode_responses=True, socket_timeout=3),
        )

    def close(self):
        self.identity.close()
        self.redis.close()
        self.database.close()

    def query(self, statement: str, parameters: tuple):
        try:
            with self.database.connection() as connection:
                return connection.execute(statement, parameters).fetchone()
        except psycopg.errors.InsufficientPrivilege as error:
            raise HTTPException(403, "Your role or assignment does not allow this action.") from error
        except psycopg.errors.NoDataFound as error:
            raise HTTPException(404, "The requested dispatch record was not found.") from error
        except (psycopg.errors.UniqueViolation, psycopg.errors.CheckViolation) as error:
            raise HTTPException(409, "This request conflicts with an existing record or active assignment.") from error
        except (psycopg.Error, PoolTimeout, PoolClosed) as error:
            raise HTTPException(503, "The dispatch database is unavailable.") from error

    def authenticate(self, access_token: str) -> Actor:
        try:
            response = self.identity.get("auth/v1/user", headers={"Authorization": f"Bearer {access_token}"})
        except httpx.RequestError as error:
            raise HTTPException(503, "Supabase Auth is unavailable.") from error
        if response.status_code in {400, 401, 403}:
            raise HTTPException(401, "Supabase rejected this access token.", headers={"WWW-Authenticate": "Bearer"})
        if response.status_code != 200:
            raise HTTPException(503, "Supabase Auth is unavailable.")
        try:
            user = response.json()
            user_id = UUID(user["id"])
        except (ValueError, TypeError, KeyError) as error:
            raise HTTPException(503, "Supabase Auth returned an unexpected response.") from error
        if user.get("is_anonymous"):
            raise HTTPException(403, "A named ClearPath account is required.")
        row = self.query("select role from clearpath.users where user_id = %s", (user_id,))
        if row is None:
            raise HTTPException(403, "This account has no ClearPath role.")
        return Actor(user_id, row[0])


def services(request: Request) -> DispatchServices:
    dispatch = getattr(request.app.state, "dispatch", None)
    if dispatch is None:
        raise HTTPException(503, "Dispatch storage is disabled on this simulator.")
    return dispatch


Services = Annotated[DispatchServices, Depends(services)]


def signed_in(
    dispatch: Services,
    authorization: Annotated[HTTPAuthorizationCredentials | None, Security(bearer)],
) -> Actor:
    if authorization is None:
        raise HTTPException(401, "A Supabase access token is required.", headers={"WWW-Authenticate": "Bearer"})
    return dispatch.authenticate(authorization.credentials)


SignedIn = Annotated[Actor, Depends(signed_in)]


class Coordinates(BaseModel):
    lat: float = Field(ge=-90, le=90, allow_inf_nan=False)
    lon: float = Field(ge=-180, le=180, allow_inf_nan=False)


class Incident(Coordinates):
    incident_id: UUID
    incident_type: Literal["medical", "fire", "police"]
    severity: int = Field(ge=1, le=5)


class Assignment(BaseModel):
    dispatch_id: UUID
    incident_id: UUID
    unit_id: UUID


class PositionSample(Coordinates):
    time_ms: int = Field(ge=0)
    nonce: UUID


class PriorityRequest(BaseModel):
    request_id: UUID
    dispatch_id: UUID
    osm_node_id: int = Field(gt=0, le=2**63 - 1)


class FreeTextReport(BaseModel):
    report: str = Field(min_length=1, max_length=1200)


class DraftReview(BaseModel):
    decision: Literal["approved", "rejected"]
    unit_ids: list[UUID] = Field(default_factory=list, max_length=3)


@router.get("/me")
def me(actor: SignedIn):
    return {"user_id": actor.user_id, "role": actor.role}


@router.get("/auth-config", include_in_schema=False)
def auth_config(dispatch: Services):
    publishable = dispatch.identity.headers.get("apikey", "")
    if not publishable.startswith("sb_publishable_"):
        raise HTTPException(503, "The Supabase publishable key is unavailable.")
    return {"project_url": str(dispatch.identity.base_url), "publishable_key": publishable}


@router.get("/board")
def board(actor: SignedIn, dispatch: Services):
    return dispatch.query("select clearpath.dispatch_board(%s)", (actor.user_id,))[0]


@router.post("/report-suggestions")
def report_suggestion(payload: FreeTextReport, actor: SignedIn, request: Request):
    if actor.role != "dispatcher":
        raise HTTPException(403, "Only a dispatcher can request a report draft.")
    model_url = os.getenv("CLEARPATH_MODEL_URL")
    if not model_url:
        raise HTTPException(503, "The local report model is disabled.")
    report = payload.report.strip()
    if not report:
        raise HTTPException(422, "Enter a report to analyze.")
    try:
        with httpx.Client(timeout=35, trust_env=False) as client:
            draft = extract_report(client, model_url, report)
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as error:
        raise HTTPException(502, "The report model did not return a valid draft.") from error
    try:
        location = verified_location(report, draft, request.app.state.router)
    except PointOutsideGraph:
        location = None
    return {"proposal": draft, "map_location": location, "requires_review": True}


@router.post("/copilot/drafts")
def draft_dispatch(payload: FreeTextReport, actor: SignedIn, dispatch: Services, request: Request):
    if actor.role != "dispatcher":
        raise HTTPException(403, "Only a dispatcher can use the copilot.")
    model_url = os.getenv("CLEARPATH_MODEL_URL")
    if not model_url:
        return {"status": "manual", "reason": "The local model is disabled.", "trace": []}
    if not payload.report.strip():
        raise HTTPException(422, "Enter an incident report.")
    simulation = request.app.state.simulation
    with simulation.lock:
        blocked = frozenset(edge for edge, road in simulation.roads.items() if road.segment in simulation.closed)

    def board():
        return dispatch.query("select clearpath.dispatch_board(%s)", (actor.user_id,))[0]

    try:
        with httpx.Client(timeout=10, trust_env=False) as client:
            result = plan_dispatch(payload.report.strip(), client, model_url, simulation.router, board, blocked)
        if result["status"] == "pending":
            draft_id = uuid4()
            dispatch.query("select clearpath.save_dispatch_draft(%s,%s,%s,%s)", (
                actor.user_id, draft_id, Jsonb(result["proposal"]), Jsonb(result["trace"]),
            ))
            result["draft_id"] = draft_id
        return result
    except HTTPException as error:
        if error.status_code != 503:
            raise
        return {"status": "manual", "reason": "Dispatch storage is unavailable.", "trace": []}


@router.post("/copilot/drafts/{draft_id}/review")
def review_dispatch(draft_id: UUID, payload: DraftReview, actor: SignedIn, dispatch: Services, request: Request):
    if actor.role != "dispatcher":
        raise HTTPException(403, "Only a dispatcher can review a draft.")
    result = dispatch.query("select clearpath.review_dispatch_draft(%s,%s,%s,%s::uuid[])", (
        actor.user_id, draft_id, payload.decision, sorted(payload.unit_ids),
    ))[0]
    simulation = request.app.state.simulation
    if simulation.dispatch_mode and result["status"] == "approved":
        current = dispatch.query("select clearpath.dispatch_board(%s)", (actor.user_id,))[0]
        incident = next((item for item in current["incidents"] if item["incident_id"] == result["incident_id"]), None)
        approved = {assignment["dispatch_id"]: assignment for assignment in result["assignments"]}
        active = [unit for unit in current["units"] if unit["dispatch_id"] in approved]
        if incident and active:
            # The rehearsal map represents one rescue vehicle. Show the ambulance first when present.
            unit = min(active, key=lambda item: (item["unit_type"] != "medical", item["unit_id"]))
            station = DEFAULT_STATIONS[unit["unit_type"]]
            origin = simulation.router.nearest_node(*LOCATIONS[station][:2])
            destination = simulation.router.nearest_node(incident["latitude"], incident["longitude"])
            label = next((name for name, point in LOCATIONS.items()
                          if simulation.router.nearest_node(*point[:2]) == destination), None)
            dispatch_id = unit["dispatch_id"]
            dispatched_at = datetime.fromisoformat(approved[dispatch_id]["dispatched_at"])
            with simulation.lock:
                simulation.launch_dispatch((dispatched_at, dispatch_id), origin, destination, label)
    return result


@router.post("/incidents")
def open_incident(payload: Incident, actor: SignedIn, dispatch: Services):
    return dispatch.query(
        "select clearpath.open_incident(%s, %s, %s, %s::smallint, %s, %s)",
        (actor.user_id, payload.incident_id, payload.incident_type, payload.severity, payload.lat, payload.lon),
    )[0]


@router.post("/incidents/{incident_id}/close")
def close_incident(incident_id: UUID, actor: SignedIn, dispatch: Services):
    return dispatch.query("select clearpath.close_incident(%s, %s)", (actor.user_id, incident_id))[0]


@router.post("/assignments")
def assign(payload: Assignment, actor: SignedIn, dispatch: Services):
    return dispatch.query(
        "select clearpath.assign_unit(%s, %s, %s, %s)",
        (actor.user_id, payload.dispatch_id, payload.incident_id, payload.unit_id),
    )[0]


@router.post("/assignments/{dispatch_id}/arrive")
def arrive(dispatch_id: UUID, actor: SignedIn, dispatch: Services):
    return dispatch.query("select clearpath.mark_arrived(%s, %s)", (actor.user_id, dispatch_id))[0]


async def position_received_ms() -> int:
    # This dependency runs before the Supabase identity and role lookups.
    return time_ns() // 1_000_000


@router.post("/position")
def position(
    payload: PositionSample,
    received_ms: Annotated[int, Depends(position_received_ms)],
    actor: SignedIn,
    dispatch: Services,
    request: Request,
):
    if actor.role not in {"rescue", "citizen"}:
        raise HTTPException(403, "Only rescue and citizen accounts can send positions.")
    if abs(received_ms - payload.time_ms) > 2000:
        raise HTTPException(409, "Position time is outside the two-second window.")
    try:
        request.app.state.router.nearest_node(payload.lat, payload.lon)
    except PointOutsideGraph as error:
        raise HTTPException(422, "Position is outside the Manhattan road graph.") from error
    user_key = f"clearpath:position:{actor.user_id}"
    try:
        outcome = dispatch.redis.eval(
            SAVE_POSITION, 2, f"{user_key}:nonce:{payload.nonce}", f"{user_key}:latest",
            payload.time_ms, payload.lat, payload.lon, payload.model_dump_json(exclude={"nonce"}),
        )
    except RedisError as error:
        raise HTTPException(503, "Temporary position storage is unavailable.") from error
    if outcome == "replay":
        raise HTTPException(409, "Duplicate or out-of-order position.")
    if outcome == "speed":
        raise HTTPException(422, "Position change exceeds the demo speed limit.")
    return {"accepted": True, "expires_in_seconds": 60}


@router.post("/preemption")
def request_preemption(payload: PriorityRequest, actor: SignedIn, dispatch: Services, request: Request):
    if actor.role != "rescue":
        raise HTTPException(403, "Only an assigned rescue account can request priority.")
    simulation = request.app.state.simulation
    if payload.osm_node_id not in simulation.signals:
        raise HTTPException(404, "The intersection is outside the signal map.")
    longitude, latitude = simulation.nodes[payload.osm_node_id]
    return dispatch.query(
        "select clearpath.record_preemption(%s, %s, %s, %s, %s, %s)",
        (actor.user_id, payload.request_id, payload.dispatch_id, payload.osm_node_id, latitude, longitude),
    )[0]
