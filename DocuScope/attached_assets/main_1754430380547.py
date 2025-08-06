import argparse
import json
from core.build_generator import generate_builds
from utils.display import display_builds, export_build_as_json

def main():
    parser = argparse.ArgumentParser(
        description="Generate Wynncraft item builds."
    )
    parser.add_argument(
        "--class",
        dest="player_class",
        type=str,
        help="Filter builds by class (e.g., archer, mage, warrior, shaman, assassin)",
    )
    parser.add_argument(
        "--max-level",
        type=int,
        help="Filter builds by maximum item level.",
    )
    parser.add_argument(
        "--playstyle",
        type=str,
        help="Filter builds by playstyle (e.g., spellspam, melee, hybrid).",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top builds to display (default: 10).",
    )
    parser.add_argument(
        "--export-json",
        type=str,
        help="Export the generated builds to a JSON file (e.g., builds.json).",
    )

    args = parser.parse_args()

    # Path to your items.json file
    items_json_path = "C:\\Users\\taish\\Desktop\\Wynncraft\\wynncli\\data\\items.json"

    print("Generating builds...")
    builds = generate_builds(
        json_path=items_json_path,
        class_filter=args.player_class,
        level_filter=args.max_level,
        playstyle_filter=args.playstyle,
        top_n=args.top,
    )

    display_builds(builds)

    if args.export_json:
        export_build_as_json(builds, args.export_json)


if __name__ == "__main__":
    main()
