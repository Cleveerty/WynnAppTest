import json

def load_items(json_path):
    """Loads item data from a JSON file."""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        return data.get('items', [])
    except FileNotFoundError:
        print(f"Error: items.json not found at {json_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_path}")
        return []

def filter_items(items, class_filter=None, level_filter=None, playstyle_filter=None):
    """Filters items based on class, level, and playstyle."""
    filtered = []
    for item in items:
        # Class compatibility
        if class_filter and class_filter not in item.get('class', []):
            continue

        # Level requirement
        if level_filter and item.get('level', 0) > level_filter:
            continue

        # Playstyle filtering (simplified for now, based on common stats)
        if playstyle_filter:
            stats = item.get('stats', {})
            if playstyle_filter == 'spellspam' and stats.get('spellDamage', 0) <= 0 and stats.get('manaRegen', 0) <= 0:
                continue
            if playstyle_filter == 'melee' and stats.get('meleeDamage', 0) <= 0:
                continue
            # Add more playstyle logic as needed

        filtered.append(item)
    return filtered
