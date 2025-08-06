"""
Build generation and validation module
"""

from itertools import combinations, product
from typing import List, Dict, Any, Optional, Tuple
import math
from . import stats

# Define item slots and their categories
WEAPON_TYPES = ['wand', 'spear', 'bow', 'dagger', 'relik']
ARMOR_TYPES = ['helmet', 'chestplate', 'leggings', 'boots']
ACCESSORY_TYPES = ['ring', 'bracelet', 'necklace']

# Class to weapon type mapping
CLASS_WEAPONS = {
    'mage': ['wand'],
    'archer': ['bow'],
    'warrior': ['spear'],
    'assassin': ['dagger'],
    'shaman': ['relik']
}

def generate_builds(items: List[Dict[str, Any]], class_choice: str, playstyle: str, 
                   elements: List[str], filters: Dict[str, Any], max_builds: int = 1000) -> List[Dict[str, Any]]:
    """Generate all viable builds based on user constraints."""
    
    # Filter items by class and type
    weapons = filter_weapons_for_class(items, class_choice)
    armor_items = {
        'helmet': [item for item in items if item.get('type') == 'helmet'],
        'chestplate': [item for item in items if item.get('type') == 'chestplate'],
        'leggings': [item for item in items if item.get('type') == 'leggings'],
        'boots': [item for item in items if item.get('type') == 'boots']
    }
    accessory_items = {
        'ring': [item for item in items if item.get('type') == 'ring'],
        'bracelet': [item for item in items if item.get('type') == 'bracelet'],
        'necklace': [item for item in items if item.get('type') == 'necklace']
    }
    
    # Apply pre-filters to reduce combinations
    weapons = apply_item_filters(weapons, filters, playstyle, elements)
    for slot in armor_items:
        armor_items[slot] = apply_item_filters(armor_items[slot], filters, playstyle, elements)
    for slot in accessory_items:
        accessory_items[slot] = apply_item_filters(accessory_items[slot], filters, playstyle, elements)
    
    # Limit items per slot to prevent explosion
    max_items_per_slot = 20
    weapons = weapons[:max_items_per_slot]
    for slot in armor_items:
        armor_items[slot] = armor_items[slot][:max_items_per_slot]
    for slot in accessory_items:
        accessory_items[slot] = accessory_items[slot][:max_items_per_slot]
    
    builds = []
    builds_checked = 0
    max_checks = 50000  # Prevent infinite loops
    
    # Generate combinations
    for weapon in weapons:
        for helmet in armor_items['helmet']:
            for chestplate in armor_items['chestplate']:
                for leggings in armor_items['leggings']:
                    for boots in armor_items['boots']:
                        # Only generate ring combinations if we have rings
                        ring_combinations = list(combinations(accessory_items['ring'], 2)) if len(accessory_items['ring']) >= 2 else [('', '')]
                        
                        for ring_combo in ring_combinations:
                            for bracelet in accessory_items['bracelet']:
                                for necklace in accessory_items['necklace']:
                                    builds_checked += 1
                                    
                                    if builds_checked > max_checks:
                                        return builds
                                    
                                    # Create build
                                    build = {
                                        'weapon': weapon,
                                        'helmet': helmet,
                                        'chestplate': chestplate,
                                        'leggings': leggings,
                                        'boots': boots,
                                        'ring1': ring_combo[0] if ring_combo[0] else None,
                                        'ring2': ring_combo[1] if ring_combo[1] else None,
                                        'bracelet': bracelet,
                                        'necklace': necklace,
                                        'class': class_choice
                                    }
                                    
                                    # Remove None values
                                    build = {k: v for k, v in build.items() if v is not None and v != ''}
                                    
                                    # Validate build
                                    if is_valid_build(build, filters):
                                        builds.append(build)
                                        
                                        if len(builds) >= max_builds:
                                            return sorted(builds, key=lambda b: calculate_build_score(b), reverse=True)
    
    # Sort builds by score
    return sorted(builds, key=lambda b: calculate_build_score(b), reverse=True)

def filter_weapons_for_class(items: List[Dict[str, Any]], class_choice: str) -> List[Dict[str, Any]]:
    """Filter weapons appropriate for the chosen class."""
    allowed_weapons = CLASS_WEAPONS.get(class_choice.lower(), WEAPON_TYPES)
    
    weapons = []
    for item in items:
        if item.get('type') in allowed_weapons:
            # Check class requirement
            class_req = item.get('classReq', '').lower()
            if not class_req or class_req == class_choice.lower():
                weapons.append(item)
    
    return weapons

def apply_item_filters(items: List[Dict[str, Any]], filters: Dict[str, Any], 
                      playstyle: str, elements: List[str]) -> List[Dict[str, Any]]:
    """Apply filters to reduce item pool."""
    filtered = items.copy()
    
    # Mythic filter
    if filters.get('no_mythics', False):
        filtered = [item for item in filtered if item.get('tier') != 'Mythic']
    
    # Level filter (allow more flexibility for builds)
    min_level = filters.get('min_level', 80)
    max_level = filters.get('max_level', 106)
    filtered = [item for item in filtered if min_level <= item.get('lvl', 0) <= max_level]
    
    # Playstyle-based filtering
    if playstyle == 'spellspam':
        # Prefer items with spell damage, mana regen, intelligence
        filtered = prioritize_by_stats(filtered, ['sdPct', 'sdRaw', 'mr', 'ms', 'int'])
    elif playstyle == 'melee':
        # Prefer items with melee damage, attack speed
        filtered = prioritize_by_stats(filtered, ['mdPct', 'mdRaw', 'atkTier', 'str', 'dex'])
    elif playstyle == 'tank':
        # Prefer items with HP, defense
        filtered = prioritize_by_stats(filtered, ['hp', 'hpBonus', 'def', 'hpr'])
    
    # Element-based filtering
    if elements:
        element_stats = []
        for element in elements:
            element_stats.extend([f'{element}DamPct', f'{element}DefPct'])
        filtered = prioritize_by_stats(filtered, element_stats, boost=True)
    
    return filtered

def prioritize_by_stats(items: List[Dict[str, Any]], preferred_stats: List[str], boost: bool = False) -> List[Dict[str, Any]]:
    """Prioritize items that have preferred stats."""
    scored_items = []
    
    for item in items:
        score = 0
        for stat in preferred_stats:
            if stat in item and item[stat] != 0:
                score += 1
        
        scored_items.append((item, score))
    
    # Sort by score, keep all items but prioritize high-scoring ones
    scored_items.sort(key=lambda x: x[1], reverse=True)
    
    # If boost is True, only keep items with at least one preferred stat
    if boost:
        scored_items = [(item, score) for item, score in scored_items if score > 0]
    
    return [item for item, score in scored_items]

def is_valid_build(build: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    """Validate a build based on constraints."""
    
    # Skill point validation
    max_sp = filters.get('max_sp', 200)
    if not validate_skill_points(build, max_sp):
        return False
    
    # Calculate basic stats for filtering
    build_stats = calculate_build_stats(build)
    
    # Apply stat filters
    if build_stats['dps'] < filters.get('min_dps', 0):
        return False
    
    if build_stats['mana'] < filters.get('min_mana_regen', 0):
        return False
    
    if filters.get('max_cost') and build_stats.get('cost', 0) > filters['max_cost']:
        return False
    
    return True

def validate_skill_points(build: Dict[str, Any], max_sp: int = 200) -> bool:
    """Validate that skill point requirements don't exceed the specified limit."""
    total_requirements = {'str': 0, 'dex': 0, 'int': 0, 'def': 0, 'agi': 0}
    
    for item in build.values():
        if isinstance(item, dict):  # Skip class string
            for stat in total_requirements:
                req_key = f'{stat}Req'
                if req_key in item:
                    total_requirements[stat] += item[req_key]
    
    # Check if any single stat exceeds reasonable limits or total exceeds max_sp
    total_points = sum(total_requirements.values())
    return total_points <= max_sp and all(req <= max_sp for req in total_requirements.values())

def calculate_build_stats(build: Dict[str, Any]) -> Dict[str, float]:
    """Calculate comprehensive build statistics."""
    
    # Initialize stats
    build_stats = {
        'dps': 0.0,
        'mana': 0.0,
        'ehp': 0.0,
        'cost': 0.0,
        'skill_points': {'str': 0, 'dex': 0, 'int': 0, 'def': 0, 'agi': 0},
        'raw_stats': {}
    }
    
    # Aggregate raw stats from all items
    raw_stats = aggregate_item_stats(build)
    build_stats['raw_stats'] = raw_stats
    
    # Calculate skill point requirements
    for item in build.values():
        if isinstance(item, dict):
            for stat in build_stats['skill_points']:
                req_key = f'{stat}Req'
                if req_key in item:
                    build_stats['skill_points'][stat] += item[req_key]
    
    # Calculate DPS (simplified spell damage calculation)
    weapon = build.get('weapon', {})
    if weapon:
        build_stats['dps'] = stats.calculate_spell_damage(
            weapon, raw_stats, build.get('class', 'mage')
        )
    
    # Calculate mana sustain
    build_stats['mana'] = stats.calculate_mana_sustain(raw_stats)
    
    # Calculate effective HP
    build_stats['ehp'] = stats.calculate_effective_hp(raw_stats, build.get('class', 'mage'))
    
    # Calculate build cost (estimate based on item tiers)
    build_stats['cost'] = calculate_build_cost(build)
    
    return build_stats

def aggregate_item_stats(build: Dict[str, Any]) -> Dict[str, float]:
    """Aggregate stats from all items in build."""
    stats = {}
    
    # Define stat keys to aggregate
    stat_keys = [
        'hp', 'hpBonus', 'mr', 'ms', 'sdPct', 'sdRaw', 'mdPct', 'mdRaw',
        'ls', 'ref', 'thorns', 'exploding', 'spd', 'atkTier', 'poison',
        'hpr', 'def', 'spPct1', 'spRaw1', 'spPct2', 'spRaw2', 'spPct3', 'spRaw3', 'spPct4', 'spRaw4',
        'rainbowRaw', 'sprint', 'sprintReg', 'jh', 'lq', 'gXp', 'gSpd',
        # Elemental damage
        'eDamPct', 'tDamPct', 'wDamPct', 'fDamPct', 'aDamPct',
        'eDefPct', 'tDefPct', 'wDefPct', 'fDefPct', 'aDefPct',
        # Skill point bonuses
        'str', 'dex', 'int', 'def', 'agi'
    ]
    
    # Initialize all stats to 0
    for key in stat_keys:
        stats[key] = 0
    
    # Aggregate from all items
    for item in build.values():
        if isinstance(item, dict):  # Skip class string
            for key in stat_keys:
                if key in item:
                    value = item[key]
                    if isinstance(value, (int, float)):
                        stats[key] += value
    
    return stats

def calculate_build_cost(build: Dict[str, Any]) -> float:
    """Estimate build cost based on item tiers and rarity."""
    cost = 0
    
    tier_costs = {
        'Normal': 0,
        'Unique': 1,
        'Rare': 5,
        'Legendary': 50,
        'Mythic': 500,
        'Fabled': 1000,
        'Set': 20
    }
    
    for item in build.values():
        if isinstance(item, dict):
            tier = item.get('tier', 'Normal')
            base_cost = tier_costs.get(tier, 0)
            
            # Adjust cost based on level
            level = item.get('lvl', 1)
            level_multiplier = max(1, level / 50)
            
            cost += base_cost * level_multiplier
    
    return cost

def calculate_build_score(build: Dict[str, Any]) -> float:
    """Calculate a score for ranking builds."""
    stats = calculate_build_stats(build)
    
    # Weighted score based on key stats
    score = (
        stats['dps'] * 0.4 +
        stats['ehp'] * 0.0001 +  # EHP is much larger, so smaller weight
        stats['mana'] * 50 +
        (120 - sum(stats['skill_points'].values())) * 10  # Bonus for unused skill points
    )
    
    return score

def optimize_build_for_playstyle(build: Dict[str, Any], playstyle: str) -> float:
    """Calculate optimization score for specific playstyle."""
    stats = calculate_build_stats(build)
    
    if playstyle == 'spellspam':
        return stats['dps'] * 0.6 + stats['mana'] * 100
    elif playstyle == 'melee':
        # For melee, we'd need to calculate melee DPS differently
        return stats['dps'] * 0.4 + stats['ehp'] * 0.0001
    elif playstyle == 'tank':
        return stats['ehp'] * 0.0002 + stats['mana'] * 20
    elif playstyle == 'hybrid':
        return stats['dps'] * 0.3 + stats['ehp'] * 0.0001 + stats['mana'] * 30
    
    return calculate_build_score(build)

def get_build_summary(build: Dict[str, Any]) -> str:
    """Generate a text summary of the build."""
    stats = calculate_build_stats(build)
    
    summary_lines = []
    summary_lines.append(f"Class: {build.get('class', 'Unknown').title()}")
    summary_lines.append(f"DPS: {stats['dps']:.0f}")
    summary_lines.append(f"Mana: {stats['mana']:.1f}/s")
    summary_lines.append(f"EHP: {stats['ehp']:.0f}")
    summary_lines.append(f"Cost: ~{stats['cost']:.0f} EB")
    
    skill_points = stats['skill_points']
    total_sp = sum(skill_points.values())
    summary_lines.append(f"Skill Points: {total_sp}/120")
    
    return "\n".join(summary_lines)
