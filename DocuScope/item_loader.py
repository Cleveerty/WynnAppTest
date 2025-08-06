"""
Wynncraft item database loader with comprehensive data processing
Loads items from WynnBuilder GitHub repository and processes all item types
"""

import json
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path
import time

class WynncraftItemLoader:
    """Loads and processes Wynncraft item data from authoritative sources"""
    
    def __init__(self):
        # Updated URL for WynnBuilder items data
        self.items_url = "https://raw.githubusercontent.com/wynnbuilder/wynnbuilder.github.io/HEAD/js/items.json"
        self.fallback_url = "https://api.wynncraft.com/v3/item/database"
        self.local_cache = Path("data/items_cache.json")
        self.items = []
        
        # Item type mappings
        self.slot_mappings = {
            'helmet': 'helmet',
            'chestplate': 'chestplate', 
            'leggings': 'leggings',
            'boots': 'boots',
            'ring': 'ring',
            'bracelet': 'bracelet',
            'necklace': 'necklace',
            'wand': 'weapon',
            'bow': 'weapon', 
            'spear': 'weapon',
            'dagger': 'weapon',
            'relik': 'weapon'
        }
        
        # Tier mappings from the reference materials
        self.tier_mappings = {
            'Normal': 'Normal',
            'Unique': 'Unique', 
            'Rare': 'Rare',
            'Legendary': 'Legendary',
            'Fabled': 'Fabled',
            'Mythic': 'Mythic',
            'Set': 'Set'
        }
        
        # Class-weapon compatibility
        self.class_weapons = {
            'mage': ['wand'],
            'archer': ['bow'],
            'warrior': ['spear'], 
            'assassin': ['dagger'],
            'shaman': ['relik']
        }

    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        Path("data").mkdir(exist_ok=True)

    def fetch_items_from_source(self) -> List[Dict[str, Any]]:
        """Fetch items from multiple sources with fallbacks"""
        # Try primary source first
        try:
            print("Fetching latest item data from WynnBuilder repository...")
            response = requests.get(self.items_url, timeout=30)
            response.raise_for_status()
            
            raw_data = response.json()
            print(f"Successfully fetched {len(raw_data)} items from WynnBuilder")
            
            # Save to cache
            self.ensure_data_directory()
            with open(self.local_cache, 'w') as f:
                json.dump(raw_data, f, indent=2)
                
            return raw_data
            
        except requests.RequestException as e:
            print(f"WynnBuilder source failed: {e}")
            
        # Try fallback source
        try:
            print("Trying fallback data source...")
            response = requests.get(self.fallback_url, timeout=30)
            response.raise_for_status()
            
            raw_data = response.json()
            
            # Handle different API response formats
            if isinstance(raw_data, dict):
                items = raw_data.get('items', raw_data.get('data', []))
            elif isinstance(raw_data, list):
                items = raw_data
            else:
                items = []
                
            print(f"Successfully fetched {len(items)} items from fallback source")
            
            # Save to cache
            self.ensure_data_directory()
            with open(self.local_cache, 'w') as f:
                json.dump(items, f, indent=2)
                
            return items
            
        except requests.RequestException as e:
            print(f"Fallback source failed: {e}")
            
        except json.JSONDecodeError as e:
            print(f"Fallback JSON parsing failed: {e}")
            
        # Load from cache as last resort
        cached_items = self.load_from_cache()
        if not cached_items:
            print("No cached data available - all sources failed")
        return cached_items

    def load_from_cache(self) -> List[Dict[str, Any]]:
        """Load items from local cache or existing data files"""
        # First try to load from cache
        if self.local_cache.exists():
            try:
                with open(self.local_cache, 'r') as f:
                    data = json.load(f)
                    if data:  # Only use cache if it has data
                        print(f"Loaded {len(data)} items from cache")
                        return data
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Cache error: {e}")
        
        # Try to load from existing items.json file
        items_file = Path("data/items.json")
        if items_file.exists():
            try:
                with open(items_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'items' in data:
                        items = data['items']
                        print(f"Loaded {len(items)} items from data/items.json")
                        return items
                    elif isinstance(data, list):
                        print(f"Loaded {len(data)} items from data/items.json")
                        return data
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading items.json: {e}")
        
        # Fallback to sample data if no other source works
        print("No cached data available, generating sample data...")
        from create_sample_data import create_sample_items
        sample_items = create_sample_items()
        
        # Save sample data to cache
        self.ensure_data_directory()
        with open(self.local_cache, 'w') as f:
            json.dump(sample_items, f, indent=2)
        
        print(f"Generated {len(sample_items)} sample items")
        return sample_items

    def normalize_item_data(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw item data into consistent format
        Handles various data formats from different Wynncraft sources
        """
        try:
            # Basic item information with fallbacks for different data formats
            item = {
                'name': raw_item.get('name', ''),
                'type': raw_item.get('type', '').lower(),
                'tier': raw_item.get('tier', raw_item.get('rarity', 'Normal')),
                'lvl': raw_item.get('lvl', raw_item.get('level', 0)),
                'category': raw_item.get('category', ''),
                'slot': self.get_item_slot(raw_item)
            }
            
            # Skill point requirements (handle both formats)
            for stat in ['str', 'dex', 'int', 'def', 'agi']:
                # Try direct stat names first, then requirement format
                req_value = raw_item.get(stat, raw_item.get(f'{stat}Req', 0))
                item[f'{stat}Req'] = req_value
                
            # Health and mana
            item['hp'] = raw_item.get('hp', 0)
            item['mana'] = raw_item.get('mana', 0)
            
            # Process identifications/stats
            identifications = {}
            
            # Direct stat mapping from Wynncraft format
            stat_mappings = {
                'hpBonus': 'health_bonus',
                'hprPct': 'health_regen_percent',
                'hprRaw': 'health_regen_raw',
                'mr': 'mana_regen',
                'ms': 'mana_steal',
                'spRaw1': 'spell_damage_raw',
                'spPct1': 'spell_damage_percent',
                'mdRaw': 'melee_damage_raw',
                'mdPct': 'melee_damage_percent',
                'ls': 'life_steal',
                'poison': 'poison',
                'thorns': 'thorns',
                'ref': 'reflection',
                'expd': 'exploding',
                'spd': 'walk_speed',
                'jh': 'jump_height',
                'lb': 'loot_bonus',
                'xpb': 'xp_bonus',
                'steal': 'stealing',
                # Direct damage percent stats
                'eDamPct': 'earth_damage_percent',
                'tDamPct': 'thunder_damage_percent',
                'wDamPct': 'water_damage_percent',
                'fDamPct': 'fire_damage_percent',
                'aDamPct': 'air_damage_percent'
            }
            
            # Map stats from raw item
            for raw_key, mapped_key in stat_mappings.items():
                if raw_key in raw_item:
                    identifications[mapped_key] = raw_item[raw_key]
            
            # Add skill point bonuses as identifications
            for stat in ['str', 'dex', 'int', 'def', 'agi']:
                bonus_value = raw_item.get(stat, 0)
                if bonus_value > 0:
                    identifications[stat] = bonus_value
                    
            if identifications:
                item['identifications'] = identifications
            
            # Weapon damage processing
            if item['category'] == 'weapon' or item['type'] in ['wand', 'bow', 'spear', 'dagger', 'relik']:
                item['damage'] = self.process_weapon_damage(raw_item)
                item['attack_speed'] = raw_item.get('atkSpd', 'Normal')
                item['slot'] = 'weapon'
            
            # Elemental defenses for armor
            if item['category'] == 'armor' or item['type'] in ['helmet', 'chestplate', 'leggings', 'boots']:
                item['defenses'] = self.process_elemental_defenses(raw_item)
            
            # Set information
            if raw_item.get('set'):
                item['set_name'] = raw_item['set']
            
            # Class requirements
            if raw_item.get('classReq'):
                item['classReq'] = raw_item['classReq'].lower()
            
            # Quest/drop requirements
            if raw_item.get('quest'):
                item['quest_req'] = raw_item['quest']
            elif raw_item.get('drop') == 'never':
                item['quest_req'] = 'Untradeable'
                item['untradeable'] = True
            
            return item
            
        except Exception as e:
            print(f"Error normalizing item {raw_item.get('name', 'Unknown')}: {e}")
            return None

    def get_item_slot(self, raw_item: Dict[str, Any]) -> str:
        """Determine equipment slot for item"""
        # Check category first (Wynncraft format)
        category = raw_item.get('category', '').lower()
        if category == 'weapon':
            return 'weapon'
        elif category == 'armor':
            return raw_item.get('type', '').lower()
        elif category == 'accessory':
            return raw_item.get('type', '').lower()
        
        # Fallback to type-based mapping
        item_type = raw_item.get('type', '').lower()
        return self.slot_mappings.get(item_type, 'unknown')

    def process_identifications(self, identifications: Dict[str, Any]) -> Dict[str, Any]:
        """Process item identifications/stats"""
        processed = {}
        
        # Common identification mappings
        id_mappings = {
            'hpBonus': 'health_bonus',
            'hprPct': 'health_regen_percent', 
            'hprRaw': 'health_regen_raw',
            'mr': 'mana_regen',
            'ms': 'mana_steal',
            'spRaw1': 'spell_damage_raw',
            'spPct1': 'spell_damage_percent',
            'mdRaw': 'melee_damage_raw',
            'mdPct': 'melee_damage_percent',
            'ls': 'life_steal',
            'poison': 'poison',
            'thorns': 'thorns',
            'ref': 'reflection',
            'expd': 'exploding',
            'spd': 'walk_speed',
            'atkTier': 'attack_speed_bonus',
            'jh': 'jump_height',
            'lootBonus': 'loot_bonus',
            'xpBonus': 'xp_bonus',
            'lb': 'loot_bonus_raw',
            'steal': 'stealing'
        }
        
        for raw_key, value in identifications.items():
            if raw_key in id_mappings:
                processed[id_mappings[raw_key]] = value
            else:
                # Keep unmapped IDs as-is
                processed[raw_key] = value
        
        return processed

    def process_weapon_damage(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        """Process weapon damage values"""
        damage = {
            'neutral': [0, 0],
            'earth': [0, 0],
            'thunder': [0, 0], 
            'water': [0, 0],
            'fire': [0, 0],
            'air': [0, 0]
        }
        
        # Damage mappings
        damage_keys = {
            'nDam': 'neutral',
            'eDam': 'earth', 
            'tDam': 'thunder',
            'wDam': 'water',
            'fDam': 'fire',
            'aDam': 'air'
        }
        
        for raw_key, damage_type in damage_keys.items():
            if raw_key in raw_item:
                damage_str = raw_item[raw_key]
                if isinstance(damage_str, str) and '-' in damage_str:
                    try:
                        min_dmg, max_dmg = map(int, damage_str.split('-'))
                        damage[damage_type] = [min_dmg, max_dmg]
                    except ValueError:
                        pass
        
        return damage

    def process_elemental_defenses(self, raw_item: Dict[str, Any]) -> Dict[str, int]:
        """Process elemental defense values"""
        defenses = {
            'earth': 0,
            'thunder': 0,
            'water': 0, 
            'fire': 0,
            'air': 0
        }
        
        defense_keys = {
            'eDef': 'earth',
            'tDef': 'thunder',
            'wDef': 'water',
            'fDef': 'fire', 
            'aDef': 'air'
        }
        
        for raw_key, defense_type in defense_keys.items():
            if raw_key in raw_item:
                defenses[defense_type] = raw_item[raw_key]
        
        return defenses

    def filter_items_by_criteria(self, items: List[Dict[str, Any]], **criteria) -> List[Dict[str, Any]]:
        """Filter items by various criteria"""
        filtered = items
        
        # Filter by level range
        if 'min_level' in criteria:
            filtered = [item for item in filtered if item.get('lvl', 0) >= criteria['min_level']]
        if 'max_level' in criteria:
            filtered = [item for item in filtered if item.get('lvl', 0) <= criteria['max_level']]
            
        # Filter by class
        if 'player_class' in criteria:
            player_class = criteria['player_class'].lower()
            if player_class in self.class_weapons:
                allowed_weapons = self.class_weapons[player_class]
                filtered = [item for item in filtered 
                           if item.get('slot') != 'weapon' or item.get('type') in allowed_weapons]
        
        # Filter by slot
        if 'slot' in criteria:
            filtered = [item for item in filtered if item.get('slot') == criteria['slot']]
        
        # Filter by tier
        if 'tier' in criteria:
            tiers = criteria['tier'] if isinstance(criteria['tier'], list) else [criteria['tier']]
            filtered = [item for item in filtered if item.get('tier') in tiers]
        
        # Filter by name search
        if 'name_search' in criteria:
            search_term = criteria['name_search'].lower()
            filtered = [item for item in filtered 
                       if search_term in item.get('name', '').lower()]
        
        return filtered

    def categorize_items(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize items by equipment slot"""
        categories = {
            'weapons': [],
            'helmets': [],
            'chestplates': [],
            'leggings': [], 
            'boots': [],
            'rings': [],
            'bracelets': [],
            'necklaces': []
        }
        
        slot_to_category = {
            'weapon': 'weapons',
            'helmet': 'helmets',
            'chestplate': 'chestplates',
            'leggings': 'leggings',
            'boots': 'boots', 
            'ring': 'rings',
            'bracelet': 'bracelets',
            'necklace': 'necklaces'
        }
        
        for item in items:
            slot = item.get('slot')
            category = slot_to_category.get(slot)
            if category:
                categories[category].append(item)
        
        return categories

    def load_items(self) -> List[Dict[str, Any]]:
        """Main method to load and process all items"""
        # Try to fetch from source, fall back to cache
        raw_items = self.fetch_items_from_source()
        
        if not raw_items:
            print("No item data available from any source")
            return []
        
        # Normalize all items
        normalized_items = []
        for raw_item in raw_items:
            normalized = self.normalize_item_data(raw_item)
            if normalized and normalized.get('name'):
                normalized_items.append(normalized)
        
        print(f"Successfully processed {len(normalized_items)} items")
        
        # Sort by level and name for consistent ordering
        normalized_items.sort(key=lambda x: (x.get('lvl', 0), x.get('name', '')))
        
        self.items = normalized_items
        return normalized_items

    def get_item_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find item by exact name match"""
        for item in self.items:
            if item.get('name', '').lower() == name.lower():
                return item
        return None

    def search_items(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search items by name (case-insensitive partial match)"""
        query = query.lower()
        matches = []
        
        for item in self.items:
            name = item.get('name', '').lower()
            if query in name:
                matches.append(item)
                if len(matches) >= limit:
                    break
        
        return matches

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self.items:
            return {}
        
        stats = {
            'total_items': len(self.items),
            'by_tier': {},
            'by_slot': {},
            'by_level': {},
            'level_range': [0, 0]
        }
        
        # Count by tier
        for item in self.items:
            tier = item.get('tier', 'Normal')
            stats['by_tier'][tier] = stats['by_tier'].get(tier, 0) + 1
        
        # Count by slot
        for item in self.items:
            slot = item.get('slot', 'unknown')
            stats['by_slot'][slot] = stats['by_slot'].get(slot, 0) + 1
        
        # Level statistics
        levels = [item.get('lvl', 0) for item in self.items if item.get('lvl', 0) > 0]
        if levels:
            stats['level_range'] = [min(levels), max(levels)]
            
            # Count by level ranges
            for level in levels:
                range_key = f"{(level // 10) * 10}-{(level // 10) * 10 + 9}"
                stats['by_level'][range_key] = stats['by_level'].get(range_key, 0) + 1
        
        return stats