"""
Statistics calculation module implementing Wynncraft damage formulas
"""

import math
from typing import Dict, Any, List, Optional, Tuple
from .loader import load_class_data

# Load class data for calculations
CLASS_DATA = load_class_data()

def calculate_spell_damage(weapon: Dict[str, Any], build_stats: Dict[str, float], class_name: str) -> float:
    """Calculate spell damage using Wynncraft damage formula."""
    
    # Get weapon base damage
    weapon_damage = get_weapon_damage(weapon)
    if weapon_damage == 0:
        return 0
    
    # Get class multipliers
    class_info = CLASS_DATA.get(class_name.lower(), CLASS_DATA['mage'])
    base_multiplier = class_info.get('baseSpellMultiplier', 1.0)
    
    # Calculate spell conversions (simplified - using average spell)
    converted_damage = apply_spell_conversions(weapon_damage, class_info.get('spellConversions', {}))
    
    # Apply percentage bonuses
    spell_damage_pct = build_stats.get('sdPct', 0) / 100
    elemental_damage_pct = get_total_elemental_damage_pct(build_stats) / 100
    
    # Apply raw damage bonuses
    raw_spell_damage = build_stats.get('sdRaw', 0)
    raw_elemental_damage = get_total_raw_elemental_damage(build_stats)
    
    # Calculate final damage
    base_damage = converted_damage * base_multiplier
    percentage_multiplier = 1 + spell_damage_pct + elemental_damage_pct
    final_damage = (base_damage * percentage_multiplier) + raw_spell_damage + raw_elemental_damage
    
    # Apply attack speed multiplier for spells
    attack_speed_multiplier = get_attack_speed_multiplier(weapon, build_stats)
    final_damage *= attack_speed_multiplier
    
    return max(0, final_damage)

def get_weapon_damage(weapon: Dict[str, Any]) -> float:
    """Extract average weapon damage."""
    # Try different damage formats
    if 'damages' in weapon:
        damages = weapon['damages']
        total_damage = 0
        
        # Sum all damage types
        damage_types = ['neutral', 'earth', 'thunder', 'water', 'fire', 'air']
        for damage_type in damage_types:
            if damage_type in damages:
                damage_range = damages[damage_type]
                if isinstance(damage_range, list) and len(damage_range) == 2:
                    avg_damage = (damage_range[0] + damage_range[1]) / 2
                    total_damage += avg_damage
        
        return total_damage
    
    # Fallback to level-based estimation
    level = weapon.get('lvl', 1)
    weapon_type = weapon.get('type', 'wand')
    
    # Base damage estimation by level and type
    base_damage_by_type = {
        'wand': level * 1.2,
        'spear': level * 1.4,
        'bow': level * 1.1,
        'dagger': level * 1.0,
        'relik': level * 1.3
    }
    
    return base_damage_by_type.get(weapon_type, level)

def apply_spell_conversions(base_damage: float, conversions: Dict[str, Dict[str, int]]) -> float:
    """Apply spell conversions to base damage."""
    if not conversions:
        return base_damage
    
    # Use average conversion (simplified approach)
    # In reality, this would depend on the specific spell being cast
    total_conversion = 0
    conversion_count = 0
    
    for spell, spell_conversions in conversions.items():
        for element, percentage in spell_conversions.items():
            total_conversion += percentage
            conversion_count += 1
    
    if conversion_count > 0:
        avg_conversion = total_conversion / conversion_count
        return base_damage * (avg_conversion / 100)
    
    return base_damage

def get_total_elemental_damage_pct(build_stats: Dict[str, float]) -> float:
    """Calculate total elemental damage percentage."""
    elemental_stats = ['eDamPct', 'tDamPct', 'wDamPct', 'fDamPct', 'aDamPct']
    return sum(build_stats.get(stat, 0) for stat in elemental_stats)

def get_total_raw_elemental_damage(build_stats: Dict[str, float]) -> float:
    """Calculate total raw elemental damage."""
    # This would need to be implemented based on weapon elemental damages
    # For now, return 0 as it's complex to calculate without full item data
    return 0

def get_attack_speed_multiplier(weapon: Dict[str, Any], build_stats: Dict[str, float]) -> float:
    """Calculate attack speed multiplier for spell damage."""
    base_attack_speed = weapon.get('atkSpd', 'NORMAL')
    attack_tier_bonus = build_stats.get('atkTier', 0)
    
    # Base multipliers by attack speed
    speed_multipliers = {
        'SUPER_SLOW': 0.51,
        'VERY_SLOW': 0.83,
        'SLOW': 1.5,
        'NORMAL': 2.05,
        'FAST': 2.5,
        'VERY_FAST': 3.1,
        'SUPER_FAST': 4.3
    }
    
    base_multiplier = speed_multipliers.get(base_attack_speed, 2.05)
    
    # Apply attack tier bonuses (each tier adds ~15% speed)
    if attack_tier_bonus != 0:
        tier_multiplier = 1 + (attack_tier_bonus * 0.15)
        base_multiplier *= tier_multiplier
    
    return base_multiplier

def calculate_effective_hp(build_stats: Dict[str, float], class_name: str) -> float:
    """Calculate effective HP accounting for defense."""
    
    # Get base HP
    base_hp = build_stats.get('hp', 0)
    hp_bonus = build_stats.get('hpBonus', 0)
    total_hp = base_hp + hp_bonus
    
    if total_hp <= 0:
        return 0
    
    # Get defense values
    defense = build_stats.get('def', 0)
    
    # Class-specific defense multipliers
    class_info = CLASS_DATA.get(class_name.lower(), CLASS_DATA['mage'])
    class_defense_multiplier = class_info.get('defenseMultiplier', 1.0)
    
    # Calculate defense multiplier (simplified formula)
    # In Wynncraft, defense reduces damage taken
    defense_multiplier = 1 + (defense * class_defense_multiplier * 0.01)
    
    # Calculate EHP
    ehp = total_hp * defense_multiplier
    
    return max(total_hp, ehp)

def calculate_mana_sustain(build_stats: Dict[str, float]) -> float:
    """Calculate mana sustain (regen + steal converted to regen)."""
    
    # Base mana regen
    mana_regen = build_stats.get('mr', 0)
    
    # Mana steal (convert to approximate regen)
    mana_steal = build_stats.get('ms', 0)
    
    # Estimate hit rate for mana steal conversion (hits per second)
    # This is a rough approximation - in reality depends on attack speed and spell usage
    estimated_hit_rate = 2.0  # hits per second
    
    # Convert mana steal to effective regen
    effective_mana_from_steal = mana_steal * estimated_hit_rate * 0.01  # Assume 1% proc chance per point
    
    total_sustain = mana_regen + effective_mana_from_steal
    
    return max(0, total_sustain)

def calculate_spell_cost(base_cost: int, intelligence: int, spell_cost_raw: int = 0, spell_cost_pct: int = 0) -> int:
    """Calculate spell cost using Wynncraft formula."""
    
    # INT percentage reduction
    int_reduction = intelligence * 0.01  # 1% per INT point
    int_reduction = min(int_reduction, 0.8)  # Cap at 80%
    
    # Apply formula: max(1, floor(ceil(cost * (1 - int %)) + spRaw) * (1 + spPct))
    step1 = math.ceil(base_cost * (1 - int_reduction))
    step2 = step1 + spell_cost_raw
    step3 = step2 * (1 + spell_cost_pct / 100)
    final_cost = max(1, math.floor(step3))
    
    return final_cost

def calculate_poison_damage(build_stats: Dict[str, float]) -> float:
    """Calculate poison damage per second."""
    poison = build_stats.get('poison', 0)
    
    # Poison deals damage every 3 seconds
    if poison > 0:
        return poison / 3
    
    return 0

def get_spell_costs_by_class(class_name: str) -> Dict[str, List[int]]:
    """Get spell costs by class (level 1, 2, 3)."""
    spell_costs = {
        'mage': {
            'heal': [8, 7, 6],
            'teleport': [4, 4, 4],
            'meteor': [8, 8, 8],
            'ice_snake': [4, 4, 4]
        },
        'archer': {
            'arrow_storm': [6, 6, 6],
            'escape': [3, 3, 3],
            'bomb': [8, 8, 8],
            'arrow_shield': [8, 9, 10]
        },
        'warrior': {
            'bash': [6, 6, 6],
            'charge': [4, 4, 4],
            'uppercut': [9, 9, 9],
            'war_scream': [6, 6, 6]
        },
        'assassin': {
            'spin_attack': [6, 6, 6],
            'vanish': [2, 2, 2],
            'multihit': [8, 8, 8],
            'smoke_bomb': [8, 8, 8]
        },
        'shaman': {
            'totem': [4, 4, 4],
            'haul': [3, 2, 1],
            'aura': [8, 8, 8],
            'uproot': [6, 6, 6]
        }
    }
    
    return spell_costs.get(class_name.lower(), {})

def calculate_dps_breakdown(weapon: Dict[str, Any], build_stats: Dict[str, float], class_name: str) -> Dict[str, float]:
    """Calculate detailed DPS breakdown."""
    
    breakdown = {
        'spell_dps': 0,
        'melee_dps': 0,
        'poison_dps': 0,
        'total_dps': 0
    }
    
    # Spell DPS
    breakdown['spell_dps'] = calculate_spell_damage(weapon, build_stats, class_name)
    
    # Poison DPS
    breakdown['poison_dps'] = calculate_poison_damage(build_stats)
    
    # Melee DPS (simplified - would need more complex calculation)
    melee_damage_pct = build_stats.get('mdPct', 0)
    if melee_damage_pct > 0:
        weapon_damage = get_weapon_damage(weapon)
        melee_multiplier = 1 + (melee_damage_pct / 100)
        attack_speed_multiplier = get_attack_speed_multiplier(weapon, build_stats)
        breakdown['melee_dps'] = weapon_damage * melee_multiplier * attack_speed_multiplier * 0.5  # Rough estimate
    
    # Total DPS
    breakdown['total_dps'] = sum(breakdown.values()) - breakdown['total_dps']  # Avoid double counting
    
    return breakdown

def calculate_survivability_score(build_stats: Dict[str, float], class_name: str) -> float:
    """Calculate a survivability score combining EHP, regen, and defensive stats."""
    
    ehp = calculate_effective_hp(build_stats, class_name)
    hp_regen = build_stats.get('hpr', 0)
    life_steal = build_stats.get('ls', 0)
    
    # Base survivability from EHP
    survivability = ehp * 0.001  # Scale down EHP
    
    # Add regeneration benefits
    survivability += hp_regen * 10  # HP regen is valuable
    survivability += life_steal * 5   # Life steal provides sustain
    
    # Add defensive resistances
    resistances = ['eDefPct', 'tDefPct', 'wDefPct', 'fDefPct', 'aDefPct']
    total_resistance = sum(build_stats.get(stat, 0) for stat in resistances)
    survivability += total_resistance * 2
    
    return survivability

def validate_stat_requirements(build: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and calculate stat requirements for a build."""
    
    requirements = {'str': 0, 'dex': 0, 'int': 0, 'def': 0, 'agi': 0}
    issues = []
    
    # Sum up requirements from all items
    for slot, item in build.items():
        if isinstance(item, dict):  # Skip class string
            for stat in requirements:
                req_key = f'{stat}Req'
                if req_key in item:
                    requirements[stat] += item[req_key]
    
    # Check total
    total_points = sum(requirements.values())
    
    if total_points > 120:
        issues.append(f"Total skill points exceed 120: {total_points}")
    
    # Check individual stat limits (items rarely require more than 120 in a single stat)
    for stat, req in requirements.items():
        if req > 120:
            issues.append(f"{stat.upper()} requirement too high: {req}")
    
    return {
        'requirements': requirements,
        'total': total_points,
        'valid': len(issues) == 0,
        'issues': issues
    }
