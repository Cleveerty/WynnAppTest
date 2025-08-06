import itertools
from core.filters import load_items, filter_items
from core.validator import is_valid_build
from core.scorer import score_build

def generate_builds(
    json_path,
    class_filter=None,
    level_filter=None,
    playstyle_filter=None,
    max_skill_points=200,
    top_n=10,
    custom_scoring_function=None
):
    """Generates, validates, scores, and sorts Wynncraft builds."""
    all_items = load_items(json_path)
    if not all_items:
        return []

    filtered_items = filter_items(
        all_items,
        class_filter=class_filter,
        level_filter=level_filter,
        playstyle_filter=playstyle_filter
    )

    # Group items by type
    items_by_type = {
        "helmet": [],
        "chestplate": [],
        "leggings": [],
        "boots": [],
        "weapon": [],
        "accessory": []
    }
    for item in filtered_items:
        item_type = item.get('type')
        if item_type in items_by_type:
            items_by_type[item_type].append(item)

    # Ensure we have at least one item for each required slot
    # Accessories are a bit special, as you can have multiple.
    # For simplicity, let's assume 3 accessory slots for now.
    # This part might need refinement based on actual game mechanics.
    required_slots = ["helmet", "chestplate", "leggings", "boots", "weapon"]
    for slot in required_slots:
        if not items_by_type[slot]:
            print(f"Warning: No items found for slot: {slot}. Cannot generate full builds.")
            return []

    # Generate combinations for accessories separately
    accessory_combinations = list(itertools.combinations(items_by_type["accessory"], 3)) if items_by_type["accessory"] else [()]

    # Generate all possible builds
    possible_builds = []
    for helmet in items_by_type["helmet"]:
        for chestplate in items_by_type["chestplate"]:
            for leggings in items_by_type["leggings"]:
                for boots in items_by_type["boots"]:
                    for weapon in items_by_type["weapon"]:
                        for accessories in accessory_combinations:
                            build = [
                                helmet,
                                chestplate,
                                leggings,
                                boots,
                                weapon,
                            ] + list(accessories)
                            possible_builds.append(build)

    valid_builds = []
    for build in possible_builds:
        if is_valid_build(build, max_skill_points):
            score = score_build(build, custom_scoring_function)
            valid_builds.append({"build": build, "score": score})

    # Sort builds by score in descending order
    valid_builds.sort(key=lambda x: x["score"], reverse=True)

    return valid_builds[:top_n]
