import os
from dataclasses import dataclass
from time import time
from typing import Annotated, Literal
from urllib.parse import urlsplit
from uuid import UUID

import httpx
import psycopg
from fastapi import APIRouter, Depends, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from psycopg.conninfo import conninfo_to_dict
from pydantic import BaseModel, Field
from redis import Redis, RedisError

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
    dsn: str
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
            dsn,
            httpx.Client(base_url=project.rstrip("/") + "/", headers={"apikey": publishable}, timeout=5),
            Redis.from_url(redis_url, decode_responses=True, socket_timeout=3),
        )

    def close(self):
        self.identity.close()
        self.redis.close()

    def query(self, statement: str, parameters: tuple):
        try:
            with psycopg.connect(
                self.dsn, connect_timeout=4, options="-c statement_timeout=5000 -c lock_timeout=3000"
            ) as connection:
                return connection.execute(statement, parameters).fetchone()
        except psycopg.errors.InsufficientPrivilege as error:
            raise HTTPException(403, "Your role or assignment does not allow this action.") from error
        except psycopg.errors.NoDataFound as error:
            raise HTTPException(404, "The requested dispatch record was not found.") from error
        except (psycopg.errors.UniqueViolation, psycopg.errors.CheckViolation) as error:
            raise HTTPException(409, "This request conflicts with an existing record or active assignment.") from error
        except psycopg.Error as error:
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


@router.get("/me")
def me(actor: SignedIn):
    return {"user_id": actor.user_id, "role": actor.role}


@router.get("/board")
def board(actor: SignedIn, dispatch: Services):
    return dispatch.query("select clearpath.dispatch_board(%s)", (actor.user_id,))[0]


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


@router.post("/position")
def position(payload: PositionSample, actor: SignedIn, dispatch: Services, request: Request):
    if actor.role not in {"rescue", "citizen"}:
        raise HTTPException(403, "Only rescue and citizen accounts can send positions.")
    if abs(time() * 1000 - payload.time_ms) > 2000:
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
