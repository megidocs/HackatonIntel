"""Geography and modeled depots for the signed-in dispatch workflow."""

from dataclasses import dataclass

from .report_extraction import LOCATIONS, LocationCatalog, UnitKind
from .scenarios import TEL_AVIV
from .tel_aviv_dispatch import FLEET


@dataclass(frozen=True)
class DispatchRegion:
    name: str
    locations: LocationCatalog
    stations: dict[UnitKind, str]
    map_url: str
    allow_catalog_fallback: bool = False

    def station(self, kind: UnitKind, reported_station: str | None = None) -> str:
        return reported_station or self.stations[kind]


MANHATTAN_REPORTS = DispatchRegion(
    "Manhattan", LOCATIONS,
    {"medical": "Bellevue Hospital", "fire": "Union Square", "police": "Times Square"},
    "/simulator",
)
TEL_AVIV_REPORTS = DispatchRegion(
    "Tel Aviv",
    {
        place.name: (place.lat, place.lon, (place.hebrew,))
        for place in (*TEL_AVIV.incidents, TEL_AVIV.origin, *(unit.base for unit in FLEET))
    },
    {"medical": "Nahmani", "fire": "Jabotinsky", "police": "Sportek"},
    "/simulator/tel-aviv/reports",
    allow_catalog_fallback=True,
)
REPORT_REGIONS = {"manhattan": MANHATTAN_REPORTS, "tel-aviv": TEL_AVIV_REPORTS}


def region_for_point(latitude: float, longitude: float) -> str:
    west, south, east, north = TEL_AVIV.bounds
    return "tel-aviv" if west <= longitude <= east and south <= latitude <= north else "manhattan"
