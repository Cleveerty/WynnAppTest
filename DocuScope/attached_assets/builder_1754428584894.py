
from itertools import combinations
from . import stats

# Define item slots
WEAPON_SLOTS = ['wand', 'spear', 'bow', 'dagger', 'relik']
ARMOR_SLOTS = ['helmet', 'chestplate', 'leggings', 'boots']
ACCESSORY_SLOTS = ['ring', 'ring', 'bracelet', 'necklace']

def generate_builds(items, class_choice, playstyle, elements, filters):
    """Generates all viable builds based on user constraints."""
    # Filter items based on the selected class and other criteria
    weapons = [item for item in items if item.get('type', '').lower() in WEAPON_SLOTS and (not item.get('classReq') or item.get('classReq') == class_choice)]
    helmets = [item for item in items if item.get('type', '').lower() == 'helmet']
    chestplates = [item for item in items if item.get('type', '').lower() == 'chestplate']
    leggings = [item for item in items if item.get('type', '').lower() == 'leggings']
    boots = [item for item in items if item.get('type', '').lower() == 'boots']
    rings = [item for item in items if item.get('type', '').lower() == 'ring']
    bracelets = [item for item in items if item.get('type', '').lower() == 'bracelet']
    necklaces = [item for item in items if item.get('type', '').lower() == 'necklace']

    # Generate all combinations of gear
    builds = []
    for weapon in weapons:
        for helmet in helmets:
            for chestplate in chestplates:
                for leggings in leggings:
                    for boots in boots:
                        for ring1, ring2 in combinations(rings, 2):
                            for bracelet in bracelets:
                                for necklace in necklaces:
                                    build = {
                                        'weapon': weapon,
                                        'helmet': helmet,
                                        'chestplate': chestplate,
                                        'leggings': leggings,
                                        'boots': boots,
                                        'ring1': ring1,
                                        'ring2': ring2,
                                        'bracelet': bracelet,
                                        'necklace': necklace,
                                    }
                                    if is_valid(build, filters):
                                        builds.append(build)
    return builds

def is_valid(build, filters):
    """Validates a build based on skill point requirements and other constraints."""
    # Simplified validation logic
    total_skill_points = 0
    for item in build.values():
        for req in ['strReq', 'dexReq', 'intReq', 'defReq', 'agiReq']:
            total_skill_points += item.get(req, 0)

    if total_skill_points > 120:
        return False

    # Add other validation checks based on filters (e.g., min mana regen, min DPS)
    return True

def calculate_build_stats(build):
    """Calculates the stats for a given build."""
    # Simplified stat calculation logic
    dps = 0
    mana = 0
    ehp = 0

    # You would need to implement the actual stat calculation based on the items in the build
    # This is just a placeholder
    for item in build.values():
        dps += item.get('sdPct', 0)  # Example: sum of spell damage percentages
        mana += item.get('mr', 0)      # Example: sum of mana regen
        ehp += item.get('hp', 0)       # Example: sum of health points

    return {'dps': dps, 'mana': mana, 'ehp': ehp}
