from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Place:
    name: str
    lon: float
    lat: float
    hebrew: str = ""


@dataclass(frozen=True)
class Scenario:
    name: str
    origin: Place
    destination: Place
    incidents: tuple[Place, ...] = ()
    landmarks: tuple[Place, ...] = ()
    bounds: tuple[float, float, float, float] | None = None


MANHATTAN = Scenario(
    "Manhattan",
    Place("Bellevue Hospital", -73.9760, 40.7391),
    Place("Times Square", -73.9855, 40.7580),
    landmarks=(
        Place("HUDSON RIVER", -74.006, 40.757),
        Place("EAST RIVER", -73.961, 40.751),
        Place("CENTRAL PARK", -73.9689, 40.7822),
    ),
)

RABIN_SQUARE = Place("Rabin Square", 34.7819, 32.0807, "כיכר רבין")
TEL_AVIV = Scenario(
    "Tel Aviv",
    Place("Ichilov Hospital", 34.7896, 32.0812, "איכילוב"),
    RABIN_SQUARE,
    incidents=(
        RABIN_SQUARE,
        Place("Dizengoff Square", 34.7747, 32.0781, "כיכר דיזנגוף"),
        Place("Habima Square", 34.7792, 32.0729, "כיכר הבימה"),
        Place("Sarona Market", 34.7871, 32.0714, "שרונה"),
    ),
    landmarks=(Place("MEDITERRANEAN SEA", 34.762, 32.081),),
    bounds=(34.758, 32.050, 34.801, 32.100),
)
TEL_AVIV_BUNDLE = Path(__file__).resolve().parent.parent / "deploy" / "tel-aviv.graphml.gz"
