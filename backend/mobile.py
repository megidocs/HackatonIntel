import asyncio
from contextlib import suppress

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .simulation import Simulation

mobile_router = APIRouter()
MAX_VIEWERS = 16


def mobile_snapshot(simulation: Simulation, role: str, vehicle_id: int) -> dict:
    with simulation.lock:
        state = {"role": role, "time": round(simulation.time, 2), "running": simulation.running}
        if role == "citizen":
            return {
                **state,
                "vehicle_id": vehicle_id,
                "assigned": vehicle_id <= len(simulation.traffic),
                "alerted": vehicle_id in simulation.priority.alerted,
            }

        return {
            **state,
            "position": simulation.vehicle_position(simulation.emergency) if simulation.emergency else None,
            "route": simulation.route_line,
            "route_status": simulation.route_status,
            "dispatch_destination": simulation.dispatch_destination,
            "route_meters": round(simulation.route_meters),
            "route_seconds": round(simulation.route_seconds),
            "priority_enabled": simulation.priority.enabled,
            "priority_signal_count": len(simulation.priority.signals),
        }


@mobile_router.websocket("/simulation/mobile")
async def mobile_stream(websocket: WebSocket):
    role = websocket.query_params.get("role")
    vehicle = websocket.query_params.get("vehicle", "1")
    if role not in {"rescue", "citizen"} or vehicle not in {"1", "2", "3", "4"}:
        await websocket.close(code=1008)
        return

    state = websocket.app.state
    viewers = getattr(state, "mobile_viewers", 0)
    if viewers >= MAX_VIEWERS:
        await websocket.close(code=1013)
        return

    state.mobile_viewers = viewers + 1
    incoming = None
    try:
        await websocket.accept()
        incoming = asyncio.create_task(websocket.receive())
        while True:
            snapshot = mobile_snapshot(state.simulation, role, int(vehicle))
            await websocket.send_json(snapshot)
            done, _ = await asyncio.wait({incoming}, timeout=.2 if snapshot["running"] else 1)
            if done:
                if incoming.result()["type"] != "websocket.disconnect":
                    await websocket.close(code=1008, reason="Read-only simulation feed")
                return
    except WebSocketDisconnect:
        pass
    finally:
        state.mobile_viewers -= 1
        if incoming is not None:
            incoming.cancel()
            with suppress(asyncio.CancelledError):
                await incoming
