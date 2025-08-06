"""
Data loader module for Wynncraft items and class information
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

def load_items() -> Optional[Dict[str, Any]]:
    """Load items from the items.json file."""
    # Try multiple possible locations
    possible_paths = [
        Path("data/items.json"),
        Path("../data/items.json"),
        Path("items.json"),
        Path(os.path.dirname(__file__)) / "../data/items.json"
    ]
    
    for file_path in possible_paths:
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Validate data structure
                    if isinstance(data, dict) and 'items' in data:
                        # Filter out items without required fields
                        valid_items = []
                        for item in data['items']:
                            if isinstance(item, dict) and 'name' in item:
                                valid_items.append(item)
                        
                        data['items'] = valid_items
                        return data
                    
                    elif isinstance(data, list):
                        # If data is directly a list of items
                        valid_items = [item for item in data if isinstance(item, dict) and 'name' in item]
                        return {'items': valid_items}
                    
                    else:
                        print(f"Warning: Unexpected data format in {file_path}")
                        continue
                        
            except json.JSONDecodeError as e:
                print(f"Error: Could not decode JSON from {file_path}: {e}")
                continue
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
    
    print("Error: items.json not found in any expected location")
    print("Expected locations:")
    for path in possible_paths:
        print(f"  - {path.absolute()}")
    
    return None

def load_class_data() -> Dict[str, Any]:
    """Load class base data."""
    class_data_path = Path("data/class_base.json")
    
    # Default class data if file doesn't exist
    default_class_data = {
        "mage": {
            "baseSpellMultiplier": 1.0,
            "spellConversions": {
                "meteor": {"earth": 30, "fire": 30},
                "ice_snake": {"water": 70},
                "teleport": {"air": 50},
                "heal": {"water": 40}
            },
            "baseDamageMultiplier": 1.0,
            "defenseMultiplier": 0.8
        },
        "archer": {
            "baseSpellMultiplier": 1.0,
            "spellConversions": {
                "arrow_storm": {"air": 40},
                "escape": {"air": 80},
                "bomb": {"fire": 100},
                "arrow_shield": {"earth": 30}
            },
            "baseDamageMultiplier": 1.1,
            "defenseMultiplier": 0.9
        },
        "warrior": {
            "baseSpellMultiplier": 0.9,
            "spellConversions": {
                "bash": {"earth": 50},
                "charge": {"earth": 30},
                "uppercut": {"thunder": 50},
                "war_scream": {"thunder": 30}
            },
            "baseDamageMultiplier": 1.2,
            "defenseMultiplier": 1.2
        },
        "assassin": {
            "baseSpellMultiplier": 1.1,
            "spellConversions": {
                "spin_attack": {"air": 40},
                "vanish": {"air": 20},
                "multihit": {"thunder": 30},
                "smoke_bomb": {"fire": 20}
            },
            "baseDamageMultiplier": 1.3,
            "defenseMultiplier": 0.7
        },
        "shaman": {
            "baseSpellMultiplier": 1.0,
            "spellConversions": {
                "totem": {"earth": 40},
                "haul": {"air": 60},
                "aura": {"water": 30},
                "uproot": {"earth": 60}
            },
            "baseDamageMultiplier": 1.0,
            "defenseMultiplier": 1.0
        }
    }
    
    if class_data_path.exists():
        try:
            with open(class_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load class data from {class_data_path}: {e}")
            print("Using default class data")
    
    return default_class_data

def get_item_by_name(items: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
    """Find an item by name."""
    for item in items:
        if item.get('name', '').lower() == name.lower():
            return item
    return None

def filter_items_by_type(items: List[Dict[str, Any]], item_type: str) -> List[Dict[str, Any]]:
    """Filter items by type."""
    return [item for item in items if item.get('type', '').lower() == item_type.lower()]

def filter_items_by_class(items: List[Dict[str, Any]], class_name: str) -> List[Dict[str, Any]]:
    """Filter items by class requirement."""
    return [
        item for item in items 
        if not item.get('classReq') or item.get('classReq', '').lower() == class_name.lower()
    ]

def filter_items_by_level(items: List[Dict[str, Any]], min_level: int = 0, max_level: int = 106) -> List[Dict[str, Any]]:
    """Filter items by level requirement."""
    return [
        item for item in items 
        if min_level <= item.get('lvl', 0) <= max_level
    ]

def get_item_categories() -> List[str]:
    """Get list of all item categories."""
    return [
        'weapon', 'helmet', 'chestplate', 'leggings', 'boots',
        'ring', 'bracelet', 'necklace', 'charm'
    ]

def get_weapon_types() -> List[str]:
    """Get list of all weapon types."""
    return ['wand', 'spear', 'bow', 'dagger', 'relik']

def validate_item_data(item: Dict[str, Any]) -> List[str]:
    """Validate item data and return list of issues."""
    issues = []
    
    required_fields = ['name', 'type']
    for field in required_fields:
        if field not in item:
            issues.append(f"Missing required field: {field}")
        elif not item[field]:
            issues.append(f"Empty required field: {field}")
    
    # Check numeric fields
    numeric_fields = ['lvl', 'strReq', 'dexReq', 'intReq', 'defReq', 'agiReq']
    for field in numeric_fields:
        if field in item and not isinstance(item[field], (int, float)):
            issues.append(f"Non-numeric value for {field}: {item[field]}")
    
    # Check level bounds
    if 'lvl' in item:
        level = item['lvl']
        if not (1 <= level <= 106):
            issues.append(f"Invalid level: {level} (must be 1-106)")
    
    return issues

def get_items_summary(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get summary statistics about the items dataset."""
    if not items:
        return {"error": "No items provided"}
    
    summary = {
        "total_items": len(items),
        "by_type": {},
        "by_tier": {},
        "by_class": {},
        "level_range": {"min": float('inf'), "max": 0},
        "validation_issues": 0
    }
    
    for item in items:
        # Count by type
        item_type = item.get('type', 'unknown')
        summary["by_type"][item_type] = summary["by_type"].get(item_type, 0) + 1
        
        # Count by tier
        tier = item.get('tier', 'Normal')
        summary["by_tier"][tier] = summary["by_tier"].get(tier, 0) + 1
        
        # Count by class requirement
        class_req = item.get('classReq', 'Any')
        summary["by_class"][class_req] = summary["by_class"].get(class_req, 0) + 1
        
        # Level range
        level = item.get('lvl', 0)
        if level > 0:
            summary["level_range"]["min"] = min(summary["level_range"]["min"], level)
            summary["level_range"]["max"] = max(summary["level_range"]["max"], level)
        
        # Validation issues
        issues = validate_item_data(item)
        if issues:
            summary["validation_issues"] += len(issues)
    
    # Fix infinite min level
    if summary["level_range"]["min"] == float('inf'):
        summary["level_range"]["min"] = 0
    
    return summary
