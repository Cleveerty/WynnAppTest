"""
Export module for Wynnbuilder compatibility
Handles build export formats and sharing
"""

import json
import urllib.parse
from typing import List, Dict, Any

def export_to_wynnbuilder(build_list: List[str]) -> str:
    """
    Export build to Wynnbuilder-compatible string format.
    
    Args:
        build_list: List containing [Class, Weapon, Helmet, Chestplate, Leggings, Boots, Ring1, Ring2, Bracelet, Necklace]
    
    Returns:
        Wynnbuilder-compatible string
    """
    if len(build_list) != 10:
        raise ValueError("Build list must contain exactly 10 items (class + 9 gear pieces)")
    
    # Format: [Class,Weapon,Helmet,Chestplate,Leggings,Boots,Ring1,Ring2,Bracelet,Necklace]
    formatted_build = "[" + ",".join(build_list) + "]"
    return formatted_build

def export_build_to_json(build: Dict[str, Any], build_stats: Dict[str, float]) -> str:
    """Export build data to JSON format."""
    export_data = {
        "build": {
            "class": build.get("class", "Unknown"),
            "items": {
                "weapon": build.get("weapon", {}).get("name", ""),
                "helmet": build.get("helmet", {}).get("name", ""),
                "chestplate": build.get("chestplate", {}).get("name", ""),
                "leggings": build.get("leggings", {}).get("name", ""),
                "boots": build.get("boots", {}).get("name", ""),
                "ring1": build.get("ring1", {}).get("name", ""),
                "ring2": build.get("ring2", {}).get("name", ""),
                "bracelet": build.get("bracelet", {}).get("name", ""),
                "necklace": build.get("necklace", {}).get("name", "")
            }
        },
        "stats": {
            "dps": round(build_stats.get("dps", 0), 2),
            "mana_sustain": round(build_stats.get("mana", 0), 2),
            "effective_hp": round(build_stats.get("ehp", 0), 2),
            "cost": round(build_stats.get("cost", 0), 2)
        },
        "skill_points": build_stats.get("skill_points", {}),
        "export_version": "1.0"
    }
    
    return json.dumps(export_data, indent=2)

def export_build_to_text(build: Dict[str, Any], build_stats: Dict[str, float], class_name: str) -> str:
    """Export build to human-readable text format."""
    lines = []
    lines.append(f"=== {class_name.title()} Build ===")
    lines.append("")
    
    # Items section
    lines.append("ITEMS:")
    item_order = ['weapon', 'helmet', 'chestplate', 'leggings', 'boots', 'ring1', 'ring2', 'bracelet', 'necklace']
    
    for slot in item_order:
        if slot in build:
            item = build[slot]
            item_name = item.get('name', 'Unknown')
            item_tier = item.get('tier', 'Normal')
            lines.append(f"  {slot.replace('1', ' 1').replace('2', ' 2').title()}: {item_name} ({item_tier})")
    
    lines.append("")
    
    # Stats section
    lines.append("STATS:")
    lines.append(f"  Spell DPS: {build_stats.get('dps', 0):.0f}")
    lines.append(f"  Mana Sustain: {build_stats.get('mana', 0):.1f}/s")
    lines.append(f"  Effective HP: {build_stats.get('ehp', 0):.0f}")
    lines.append(f"  Build Cost: {build_stats.get('cost', 0):.0f} Emerald Blocks")
    
    lines.append("")
    
    # Skill points section
    skill_points = build_stats.get('skill_points', {})
    if skill_points:
        lines.append("SKILL POINTS:")
        total_sp = 0
        for stat, value in skill_points.items():
            if value > 0:
                lines.append(f"  {stat.upper()}: {value}")
                total_sp += value
        lines.append(f"  TOTAL: {total_sp}/120")
    
    lines.append("")
    
    # Wynnbuilder export
    try:
        build_list = [class_name.title()]
        for slot in item_order:
            build_list.append(build[slot].get('name', '') if slot in build else '')
        
        wynnbuilder_string = export_to_wynnbuilder(build_list)
        lines.append("WYNNBUILDER EXPORT:")
        lines.append(wynnbuilder_string)
    except Exception as e:
        lines.append(f"WYNNBUILDER EXPORT: Error generating export string: {e}")
    
    return "\n".join(lines)

def create_wynnbuilder_url(build_list: List[str]) -> str:
    """Create a Wynnbuilder URL for the build."""
    try:
        build_string = export_to_wynnbuilder(build_list)
        # URL encode the build string
        encoded_build = urllib.parse.quote(build_string)
        
        # Wynnbuilder URL format (this is a placeholder - actual URL format may vary)
        base_url = "https://wynnbuilder.github.io/"
        return f"{base_url}?build={encoded_build}"
    
    except Exception as e:
        return f"Error creating URL: {e}"

def validate_build_export(build: Dict[str, Any]) -> List[str]:
    """Validate build data before export."""
    errors = []
    
    required_slots = ['weapon', 'helmet', 'chestplate', 'leggings', 'boots', 'ring1', 'ring2', 'bracelet', 'necklace']
    
    for slot in required_slots:
        if slot not in build:
            errors.append(f"Missing {slot}")
        elif not build[slot].get('name'):
            errors.append(f"Invalid {slot} - missing name")
    
    return errors

def export_multiple_builds(builds: List[Dict[str, Any]], class_name: str, filename: str = "builds_export.txt") -> bool:
    """Export multiple builds to a single file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"WynnBuilder CLI Export - {class_name.title()} Builds\n")
            f.write("=" * 50 + "\n\n")
            
            for i, build in enumerate(builds, 1):
                from core.builder import calculate_build_stats
                build_stats = calculate_build_stats(build)
                
                f.write(f"BUILD #{i}\n")
                f.write("-" * 20 + "\n")
                
                build_text = export_build_to_text(build, build_stats, class_name)
                f.write(build_text)
                f.write("\n\n")
        
        return True
    
    except Exception as e:
        print(f"Error exporting builds: {e}")
        return False

# Build sharing utilities
def create_build_hash(build: Dict[str, Any]) -> str:
    """Create a hash for build identification."""
    import hashlib
    
    # Create a string representation of the build
    build_items = []
    item_order = ['weapon', 'helmet', 'chestplate', 'leggings', 'boots', 'ring1', 'ring2', 'bracelet', 'necklace']
    
    for slot in item_order:
        if slot in build:
            build_items.append(build[slot].get('name', ''))
        else:
            build_items.append('')
    
    build_string = "|".join(build_items)
    return hashlib.md5(build_string.encode()).hexdigest()[:8]

def parse_wynnbuilder_string(build_string: str) -> List[str]:
    """Parse a Wynnbuilder export string back to build list."""
    try:
        # Remove brackets and split by commas
        clean_string = build_string.strip('[]')
        return [item.strip() for item in clean_string.split(',')]
    
    except Exception as e:
        raise ValueError(f"Invalid Wynnbuilder string format: {e}")
