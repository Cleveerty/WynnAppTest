"""
Advanced filtering system for items and builds
"""

from typing import List, Dict, Any, Optional, Callable
import re

def filter_items(items: List[Dict[str, Any]], class_filter: Optional[str] = None,
                playstyle_filter: Optional[str] = None, element_filter: Optional[List[str]] = None,
                no_mythics: bool = False, level_range: Optional[tuple] = None,
                custom_filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Advanced item filtering with multiple criteria."""
    
    filtered = items.copy()
    
    # Class requirement filter
    if class_filter:
        filtered = apply_class_filter(filtered, class_filter)
    
    # Mythic filter
    if no_mythics:
        filtered = apply_tier_filter(filtered, exclude_tiers=['Mythic'])
    
    # Level range filter
    if level_range:
        min_level, max_level = level_range
        filtered = apply_level_filter(filtered, min_level, max_level)
    
    # Playstyle filter
    if playstyle_filter:
        filtered = apply_playstyle_filter(filtered, playstyle_filter)
    
    # Element filter
    if element_filter:
        filtered = apply_element_filter(filtered, element_filter)
    
    # Custom filters
    if custom_filters:
        filtered = apply_custom_filters(filtered, custom_filters)
    
    return filtered

def apply_class_filter(items: List[Dict[str, Any]], class_name: str) -> List[Dict[str, Any]]:
    """Filter items by class requirement."""
    class_name = class_name.lower()
    
    return [
        item for item in items
        if not item.get('classReq') or item.get('classReq', '').lower() == class_name
    ]

def apply_tier_filter(items: List[Dict[str, Any]], include_tiers: Optional[List[str]] = None,
                     exclude_tiers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Filter items by tier/rarity."""
    
    if include_tiers:
        return [item for item in items if item.get('tier') in include_tiers]
    
    if exclude_tiers:
        return [item for item in items if item.get('tier') not in exclude_tiers]
    
    return items

def apply_level_filter(items: List[Dict[str, Any]], min_level: int = 0, max_level: int = 106) -> List[Dict[str, Any]]:
    """Filter items by level requirement."""
    return [
        item for item in items
        if min_level <= item.get('lvl', 0) <= max_level
    ]

def apply_playstyle_filter(items: List[Dict[str, Any]], playstyle: str) -> List[Dict[str, Any]]:
    """Filter items based on playstyle preferences."""
    
    playstyle = playstyle.lower()
    
    if playstyle == 'spellspam':
        return filter_for_spellspam(items)
    elif playstyle == 'melee':
        return filter_for_melee(items)
    elif playstyle == 'tank':
        return filter_for_tank(items)
    elif playstyle == 'hybrid':
        return filter_for_hybrid(items)
    
    return items

def filter_for_spellspam(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter items suitable for spellspam builds."""
    scored_items = []
    
    for item in items:
        score = 0
        
        # High value stats for spellspam
        if item.get('sdPct', 0) > 0:
            score += 3
        if item.get('sdRaw', 0) > 0:
            score += 2
        if item.get('mr', 0) > 0:
            score += 3
        if item.get('ms', 0) > 0:
            score += 2
        if item.get('int', 0) > 0:
            score += 2
        
        # Elemental damage bonuses
        elemental_stats = ['eDamPct', 'tDamPct', 'wDamPct', 'fDamPct', 'aDamPct']
        for stat in elemental_stats:
            if item.get(stat, 0) > 0:
                score += 1
        
        # Negative score for unwanted stats
        if item.get('mdPct', 0) > 15:  # Too much melee focus
            score -= 1
        
        scored_items.append((item, score))
    
    # Sort by score and return items with positive scores
    scored_items.sort(key=lambda x: x[1], reverse=True)
    return [item for item, score in scored_items if score >= 0]

def filter_for_melee(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter items suitable for melee builds."""
    scored_items = []
    
    for item in items:
        score = 0
        
        # High value stats for melee
        if item.get('mdPct', 0) > 0:
            score += 3
        if item.get('mdRaw', 0) > 0:
            score += 2
        if item.get('atkTier', 0) > 0:
            score += 2
        if item.get('str', 0) > 0:
            score += 2
        if item.get('dex', 0) > 0:
            score += 2
        
        # Secondary useful stats
        if item.get('ls', 0) > 0:
            score += 1
        if item.get('hp', 0) > 0:
            score += 1
        
        scored_items.append((item, score))
    
    scored_items.sort(key=lambda x: x[1], reverse=True)
    return [item for item, score in scored_items if score >= 0]

def filter_for_tank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter items suitable for tank builds."""
    scored_items = []
    
    for item in items:
        score = 0
        
        # High value stats for tank
        if item.get('hp', 0) > 0:
            score += 3
        if item.get('hpBonus', 0) > 0:
            score += 2
        if item.get('def', 0) > 0:
            score += 3
        if item.get('hpr', 0) > 0:
            score += 2
        
        # Defensive elemental stats
        defensive_stats = ['eDefPct', 'tDefPct', 'wDefPct', 'fDefPct', 'aDefPct']
        for stat in defensive_stats:
            if item.get(stat, 0) > 0:
                score += 1
        
        # Negative score for glass cannon stats
        if item.get('hp', 0) < 0:
            score -= 2
        if item.get('def', 0) < 0:
            score -= 2
        
        scored_items.append((item, score))
    
    scored_items.sort(key=lambda x: x[1], reverse=True)
    return [item for item, score in scored_items if score >= 0]

def filter_for_hybrid(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter items suitable for hybrid builds."""
    scored_items = []
    
    for item in items:
        score = 0
        
        # Balanced stats
        if item.get('sdPct', 0) > 0 and item.get('mdPct', 0) > 0:
            score += 3  # Items with both spell and melee damage
        
        if item.get('hp', 0) > 0:
            score += 1
        if item.get('mr', 0) > 0:
            score += 1
        
        # Multi-stat items are good for hybrid
        stat_count = sum(1 for stat in ['str', 'dex', 'int', 'def', 'agi'] if item.get(stat, 0) > 0)
        score += stat_count
        
        scored_items.append((item, score))
    
    scored_items.sort(key=lambda x: x[1], reverse=True)
    return [item for item, score in scored_items]

def apply_element_filter(items: List[Dict[str, Any]], elements: List[str]) -> List[Dict[str, Any]]:
    """Filter items based on elemental preferences."""
    if not elements:
        return items
    
    scored_items = []
    
    # Map element names to stat keys
    element_map = {
        'earth': ['eDamPct', 'eDefPct'],
        'thunder': ['tDamPct', 'tDefPct'],
        'water': ['wDamPct', 'wDefPct'],
        'fire': ['fDamPct', 'fDefPct'],
        'air': ['aDamPct', 'aDefPct']
    }
    
    preferred_stats = []
    for element in elements:
        element = element.lower()
        if element in element_map:
            preferred_stats.extend(element_map[element])
    
    for item in items:
        score = 0
        
        # Score based on preferred elemental stats
        for stat in preferred_stats:
            if item.get(stat, 0) > 0:
                score += 2
        
        # Neutral items (no elemental focus) get base score
        if score == 0:
            score = 1
        
        scored_items.append((item, score))
    
    scored_items.sort(key=lambda x: x[1], reverse=True)
    return [item for item, score in scored_items if score > 0]

def apply_custom_filters(items: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply custom filters based on specific requirements."""
    filtered = items.copy()
    
    # Minimum stat requirements
    for stat, min_value in filters.items():
        if stat.startswith('min_'):
            stat_key = stat[4:]  # Remove 'min_' prefix
            filtered = [item for item in filtered if item.get(stat_key, 0) >= min_value]
        elif stat.startswith('max_'):
            stat_key = stat[4:]  # Remove 'max_' prefix
            filtered = [item for item in filtered if item.get(stat_key, 0) <= min_value]
    
    # Name pattern filter
    if 'name_pattern' in filters:
        pattern = filters['name_pattern']
        filtered = [item for item in filtered if re.search(pattern, item.get('name', ''), re.IGNORECASE)]
    
    # Exclude specific items
    if 'exclude_items' in filters:
        exclude_names = filters['exclude_items']
        filtered = [item for item in filtered if item.get('name') not in exclude_names]
    
    # Include only specific items
    if 'include_items' in filters:
        include_names = filters['include_items']
        filtered = [item for item in filtered if item.get('name') in include_names]
    
    return filtered

def create_item_score_function(preferences: Dict[str, float]) -> Callable[[Dict[str, Any]], float]:
    """Create a custom scoring function based on stat preferences."""
    
    def score_item(item: Dict[str, Any]) -> float:
        score = 0
        for stat, weight in preferences.items():
            value = item.get(stat, 0)
            if isinstance(value, (int, float)):
                score += value * weight
        return score
    
    return score_item

def filter_by_score(items: List[Dict[str, Any]], score_function: Callable[[Dict[str, Any]], float],
                   min_score: float = 0, top_n: Optional[int] = None) -> List[Dict[str, Any]]:
    """Filter items by a custom scoring function."""
    
    scored_items = [(item, score_function(item)) for item in items]
    
    # Filter by minimum score
    if min_score > 0:
        scored_items = [(item, score) for item, score in scored_items if score >= min_score]
    
    # Sort by score
    scored_items.sort(key=lambda x: x[1], reverse=True)
    
    # Limit to top N
    if top_n:
        scored_items = scored_items[:top_n]
    
    return [item for item, score in scored_items]

def get_filter_presets() -> Dict[str, Dict[str, Any]]:
    """Get predefined filter presets for common build types."""
    return {
        'glass_cannon': {
            'min_sdPct': 50,
            'exclude_items': [],
            'playstyle': 'spellspam'
        },
        'budget_build': {
            'exclude_tiers': ['Mythic', 'Legendary'],
            'max_lvl': 80
        },
        'endgame': {
            'min_lvl': 95,
            'include_tiers': ['Legendary', 'Mythic']
        },
        'balanced': {
            'min_hp': 1000,
            'min_mr': 3,
            'playstyle': 'hybrid'
        }
    }

def apply_filter_preset(items: List[Dict[str, Any]], preset_name: str) -> List[Dict[str, Any]]:
    """Apply a predefined filter preset."""
    presets = get_filter_presets()
    
    if preset_name not in presets:
        raise ValueError(f"Unknown preset: {preset_name}")
    
    preset = presets[preset_name]
    
    return filter_items(
        items,
        playstyle_filter=preset.get('playstyle'),
        no_mythics='Mythic' in preset.get('exclude_tiers', []),
        level_range=(preset.get('min_lvl', 0), preset.get('max_lvl', 106)),
        custom_filters=preset
    )
