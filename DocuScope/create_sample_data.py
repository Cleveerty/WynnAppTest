#!/usr/bin/env python3
"""
Create sample item data for testing the WynnBuilder CLI
Based on authentic Wynncraft item information from reference materials
"""

import json
from pathlib import Path

def create_sample_items():
    """Create sample items based on the reference materials provided"""
    
    # Sample items based on the extensive reference materials
    sample_items = [
        # Legendary Wands
        {
            "name": "Prymari",
            "type": "wand",
            "tier": "Legendary",
            "lvl": 76,
            "slot": "weapon",
            "strReq": 0,
            "dexReq": 25,
            "intReq": 25,
            "defReq": 25,
            "agiReq": 0,
            "hp": 0,
            "mana": 0,
            "damage": {
                "neutral": [60, 100],
                "earth": [0, 0],
                "thunder": [20, 33],
                "water": [20, 33],
                "fire": [20, 33],
                "air": [0, 0]
            },
            "attack_speed": "Normal",
            "identifications": {
                "spell_damage_percent": 15,
                "mana_regen": 5
            }
        },
        
        # Mythic Spear
        {
            "name": "Guardian",
            "type": "spear", 
            "tier": "Mythic",
            "lvl": 93,
            "slot": "weapon",
            "strReq": 0,
            "dexReq": 0,
            "intReq": 0,
            "defReq": 110,
            "agiReq": 0,
            "hp": 0,
            "mana": 0,
            "damage": {
                "neutral": [50, 90],
                "earth": [0, 0],
                "thunder": [0, 0],
                "water": [0, 0],
                "fire": [165, 205],
                "air": [0, 0]
            },
            "attack_speed": "Normal",
            "identifications": {
                "health_bonus": 2000,
                "spell_damage_percent": 25
            }
        },
        
        # Fabled Helmet
        {
            "name": "Ornate Shadow Cowl",
            "type": "helmet",
            "tier": "Fabled", 
            "lvl": 103,
            "slot": "helmet",
            "strReq": 0,
            "dexReq": 0,
            "intReq": 0,
            "defReq": 0,
            "agiReq": 0,
            "hp": 4000,
            "mana": 0,
            "defenses": {
                "earth": 100,
                "thunder": 100,
                "water": 0,
                "fire": 0,
                "air": 0
            },
            "identifications": {
                "health_bonus": 500,
                "walk_speed": 10
            },
            "quest_req": "A Hunter's Calling",
            "untradeable": True
        },
        
        # Unique Items (common tier)
        {
            "name": "Nemract's Bow",
            "type": "bow",
            "tier": "Unique",
            "lvl": 7,
            "slot": "weapon",
            "strReq": 0,
            "dexReq": 0,
            "intReq": 0,
            "defReq": 0,
            "agiReq": 0,
            "hp": 0,
            "mana": 0,
            "damage": {
                "neutral": [12, 23],
                "earth": [0, 0],
                "thunder": [0, 0],
                "water": [0, 0],
                "fire": [0, 0],
                "air": [0, 0]
            },
            "attack_speed": "Slow",
            "identifications": {
                "melee_damage_percent": 8
            }
        },
        
        # Set Item - Leaf Set
        {
            "name": "Leaf Cap",
            "type": "helmet",
            "tier": "Set",
            "lvl": 2,
            "slot": "helmet",
            "strReq": 0,
            "dexReq": 0,
            "intReq": 0,
            "defReq": 0,
            "agiReq": 0,
            "hp": 9,
            "mana": 0,
            "defenses": {
                "earth": 2,
                "thunder": 0,
                "water": 0,
                "fire": 0,
                "air": 0
            },
            "identifications": {
                "health_regen_percent": 5,
                "health_regen_raw": 1
            },
            "set_name": "Leaf"
        },
        
        # Normal Item
        {
            "name": "Oak Wood Bow",
            "type": "bow",
            "tier": "Normal",
            "lvl": 1,
            "slot": "weapon",
            "strReq": 0,
            "dexReq": 0,
            "intReq": 0,
            "defReq": 0,
            "agiReq": 0,
            "hp": 0,
            "mana": 0,
            "damage": {
                "neutral": [5, 13],
                "earth": [0, 0],
                "thunder": [0, 0],
                "water": [0, 0],
                "fire": [0, 0],
                "air": [0, 0]
            },
            "attack_speed": "Slow"
        },
        
        # Accessories
        {
            "name": "Gylia Ring",
            "type": "ring",
            "tier": "Unique",
            "lvl": 15,
            "slot": "ring",
            "strReq": 0,
            "dexReq": 0,
            "intReq": 5,
            "defReq": 0,
            "agiReq": 0,
            "hp": 0,
            "mana": 20,
            "identifications": {
                "mana_regen": 2,
                "spell_damage_percent": 5
            }
        },
        
        {
            "name": "Slime Ring",
            "type": "ring", 
            "tier": "Set",
            "lvl": 5,
            "slot": "ring",
            "strReq": 3,
            "dexReq": 0,
            "intReq": 0,
            "defReq": 0,
            "agiReq": 0,
            "hp": 15,
            "mana": 0,
            "identifications": {
                "health_regen_raw": 1,
                "poison": 5
            },
            "set_name": "Slime"
        },
        
        # High-level armor pieces
        {
            "name": "Crusade Sabatons",
            "type": "boots",
            "tier": "Mythic",
            "lvl": 90,
            "slot": "boots",
            "strReq": 60,
            "dexReq": 0,
            "intReq": 0,
            "defReq": 70,
            "agiReq": 0,
            "hp": 5050,
            "mana": 0,
            "defenses": {
                "earth": 125,
                "thunder": 0,
                "water": 0,
                "fire": 200,
                "air": 0
            },
            "identifications": {
                "health_bonus": 1000,
                "walk_speed": 15
            }
        },
        
        {
            "name": "Gale's Force",
            "type": "bow",
            "tier": "Legendary", 
            "lvl": 95,
            "slot": "weapon",
            "strReq": 0,
            "dexReq": 30,
            "intReq": 0,
            "defReq": 0,
            "agiReq": 70,
            "hp": 0,
            "mana": 0,
            "damage": {
                "neutral": [120, 150],
                "earth": [0, 0],
                "thunder": [0, 0],
                "water": [0, 0],
                "fire": [0, 0],
                "air": [120, 150]
            },
            "attack_speed": "Very Fast",
            "identifications": {
                "melee_damage_percent": 20,
                "walk_speed": 12
            }
        }
    ]
    
    return sample_items

def main():
    """Create sample data files"""
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Create sample items
    items = create_sample_items()
    
    # Save to cache file
    cache_file = data_dir / "items_cache.json"
    with open(cache_file, 'w') as f:
        json.dump(items, f, indent=2)
    
    print(f"Created sample data with {len(items)} items in {cache_file}")
    
    # Show summary
    print("\nSample data summary:")
    tiers = {}
    for item in items:
        tier = item.get('tier', 'Unknown')
        tiers[tier] = tiers.get(tier, 0) + 1
    
    for tier, count in tiers.items():
        print(f"  {tier}: {count} items")

if __name__ == "__main__":
    main()