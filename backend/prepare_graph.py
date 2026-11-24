import argparse
from pathlib import Path
from tempfile import NamedTemporaryFile

import osmnx as ox
from shapely.geometry import box

from .routing import DEFAULT_GRAPH_PATH
from .scenarios import TEL_AVIV

MANHATTAN_PLACE = "Manhattan, New York City, New York, USA"


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare an OSM driving graph for the simulator.")
    parser.add_argument("--city", choices=("manhattan", "tel-aviv"), default="manhattan")
    parser.add_argument("--output", type=Path)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--overpass-url", help="Override the base URL of the Overpass API.")
    source.add_argument("--pbf", type=Path, help="Build from a regional OSM PBF extract.")
    args = parser.parse_args()
    tel_aviv = args.city == "tel-aviv"
    place = TEL_AVIV.name if tel_aviv else MANHATTAN_PLACE
    args.output = args.output or DEFAULT_GRAPH_PATH.with_name(f"{args.city}.graphml")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    ox.settings.cache_folder = args.output.parent / "osm-cache"
    ox.settings.requests_timeout = 60
    ox.settings.http_user_agent = (
        "ClearPathAI-HackatonIntel/0.1 (https://github.com/megidocs/HackatonIntel)"
    )
    if args.overpass_url:
        ox.settings.overpass_url = args.overpass_url

    if args.pbf:
        print(f"Reading the driving network from {args.pbf}.", flush=True)
        boundary = box(*TEL_AVIV.bounds) if tel_aviv else ox.geocoder.geocode_to_gdf(place).geometry.iloc[0]
        graph = ox.graph.graph_from_pbf(args.pbf, network_type="drive", simplify=False)
        graph = ox.truncate.truncate_graph_polygon(graph, boundary)
        graph = ox.truncate.largest_component(graph)
        graph = ox.simplification.simplify_graph(graph, node_attrs_include=["highway"] if tel_aviv else None)
    else:
        print(f"Fetching the driving network for {place}.", flush=True)
        if tel_aviv:
            graph = ox.graph.graph_from_bbox(TEL_AVIV.bounds, network_type="drive", simplify=False)
            graph = ox.simplification.simplify_graph(graph, node_attrs_include=["highway"])
        else:
            graph = ox.graph.graph_from_place(place, network_type="drive")
    ox.routing.add_edge_speeds(graph)
    ox.routing.add_edge_travel_times(graph)

    with NamedTemporaryFile(dir=args.output.parent, suffix=".graphml", delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        ox.io.save_graphml(graph, temporary_path)
        temporary_path.replace(args.output)
    finally:
        temporary_path.unlink(missing_ok=True)
    print(f"Saved {len(graph):,} nodes and {graph.number_of_edges():,} directed edges to {args.output}.")


if __name__ == "__main__":
    main()
