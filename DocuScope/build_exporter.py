"""
Build export system for Wynncraft builds
Supports JSON, Wynnbuilder import strings, and text summaries
"""

import json
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime

class WynncraftBuildExporter:
    """Exports Wynncraft builds in various formats"""
    
    def __init__(self):
        # Equipment slot mappings for export
        self.slot_mappings = {
            'helmet': 'helmet',
            'chestplate': 'chestplate',
            'leggings': 'leggings', 
            'boots': 'boots',
            'weapon': 'weapon',
            'ring': 'ring1',  # First ring
            'ring2': 'ring2', # Second ring  
            'bracelet': 'bracelet',
            'necklace': 'necklace'
        }

    def export_json(self, items: List[Dict[str, Any]], player_class: str = None, 
                   build_name: str = None) -> Dict[str, Any]:
        """
        Export build as JSON format
        
        Args:
            items: List of equipped items
            player_class: Player's class
            build_name: Optional build name
            
        Returns:
            Dictionary with build data
        """
        export_data = {
            'format_version': '1.0',
            'export_timestamp': datetime.now().isoformat(),
            'build_name': build_name or f"{player_class or 'Unknown'} Build",
            'player_class': player_class,
            'items': {},
            'metadata': {
                'total_items': len(items),
                'exporter': 'WynnBuilder CLI'
            }
        }
        
        # Organize items by slot
        for item in items:
            slot = item.get('slot', 'unknown')
            item_name = item.get('name', 'Unknown')
            
            # Handle multiple rings
            if slot == 'ring':
                if 'ring1' not in export_data['items']:
                    export_data['items']['ring1'] = {
                        'name': item_name,
                        'data': item
                    }
                else:
                    export_data['items']['ring2'] = {
                        'name': item_name,
                        'data': item
                    }
            else:
                export_data['items'][slot] = {
                    'name': item_name,
                    'data': item
                }
        
        return export_data

    def export_wynnbuilder_url(self, items: List[Dict[str, Any]], player_class: str = None) -> str:
        """
        Generate Wynnbuilder-compatible import URL
        
        Args:
            items: List of equipped items
            player_class: Player's class
            
        Returns:
            Wynnbuilder import URL
        """
        # Create build data structure compatible with Wynnbuilder
        build_data = {
            'version': 9,  # Wynnbuilder format version
            'class': self._get_class_number(player_class) if player_class else 0,
            'items': {}
        }
        
        # Map items to Wynnbuilder format
        for item in items:
            slot = item.get('slot', 'unknown')
            item_name = item.get('name', '')
            
            if slot in self.slot_mappings:
                wynnbuilder_slot = self.slot_mappings[slot]
                
                # Handle duplicate rings
                if slot == 'ring':
                    if 'ring1' not in build_data['items']:
                        build_data['items']['ring1'] = item_name
                    else:
                        build_data['items']['ring2'] = item_name
                else:
                    build_data['items'][wynnbuilder_slot] = item_name
        
        # Encode as base64 for URL
        json_str = json.dumps(build_data, separators=(',', ':'))
        encoded = base64.b64encode(json_str.encode()).decode()
        
        return f"https://wynnbuilder.github.io/#9_{encoded}"

    def export_text_summary(self, items: List[Dict[str, Any]], player_class: str = None, 
                          stats: Dict[str, Any] = None) -> str:
        """
        Export build as formatted text summary
        
        Args:
            items: List of equipped items
            player_class: Player's class
            stats: Optional build statistics
            
        Returns:
            Formatted text summary
        """
        lines = []
        lines.append("=" * 60)
        lines.append(f"WYNNCRAFT BUILD SUMMARY")
        lines.append("=" * 60)
        
        if player_class:
            lines.append(f"Class: {player_class.title()}")
            
        lines.append(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Equipment section
        lines.append("EQUIPMENT:")
        lines.append("-" * 40)
        
        slot_order = ['weapon', 'helmet', 'chestplate', 'leggings', 'boots', 
                     'ring', 'ring2', 'bracelet', 'necklace']
        
        equipped_by_slot = {}
        for item in items:
            slot = item.get('slot', 'unknown')
            if slot == 'ring':
                if 'ring' not in equipped_by_slot:
                    equipped_by_slot['ring'] = item
                else:
                    equipped_by_slot['ring2'] = item
            else:
                equipped_by_slot[slot] = item
        
        for slot in slot_order:
            if slot in equipped_by_slot:
                item = equipped_by_slot[slot]
                name = item.get('name', 'Unknown')
                level = item.get('lvl', 0)
                tier = item.get('tier', 'Normal')
                
                slot_display = slot.replace('ring2', 'Ring 2').title()
                lines.append(f"  {slot_display:12} {name} (Lv.{level} {tier})")
        
        # Statistics section
        if stats:
            lines.append("")
            lines.append("STATISTICS:")
            lines.append("-" * 40)
            
            if 'health' in stats:
                health = stats['health']
                lines.append(f"  Health:      {health.get('total', 0)} HP")
                lines.append(f"  Health Regen: {health.get('regen_per_5s', 0)}/5s")
            
            if 'mana' in stats:
                mana = stats['mana']
                lines.append(f"  Mana:        {mana.get('total', 0)}")
                lines.append(f"  Mana Regen:  {mana.get('regen_per_5s', 0)}/5s")
            
            if 'skill_points' in stats:
                sp = stats['skill_points']
                total_sp = sum(sp.values()) if sp else 0
                lines.append(f"  Skill Points: {total_sp}/200")
                if sp:
                    lines.append(f"    STR: {sp.get('str', 0)}, DEX: {sp.get('dex', 0)}, INT: {sp.get('int', 0)}")
                    lines.append(f"    DEF: {sp.get('def', 0)}, AGI: {sp.get('agi', 0)}")
            
            if 'effective_hp' in stats:
                ehp = stats['effective_hp']
                lines.append(f"  Effective HP: {ehp.get('combined_ehp', 0)}")
            
            if 'damage' in stats:
                damage = stats['damage']
                lines.append(f"  Main Attack DPS: {damage.get('main_attack_dps', 0):.1f}")
        
        lines.append("")
        lines.append("=" * 60)
        lines.append("Generated by WynnBuilder CLI")
        lines.append("=" * 60)
        
        return "\n".join(lines)

    def export_wynndata_format(self, items: List[Dict[str, Any]], player_class: str = None) -> Dict[str, Any]:
        """
        Export in WynnData API compatible format
        
        Args:
            items: List of equipped items
            player_class: Player's class
            
        Returns:
            WynnData compatible build structure
        """
        wynndata_build = {
            'type': 'build',
            'class': player_class,
            'level': 106,  # Default max level
            'items': [],
            'skills': {
                'strength': 0,
                'dexterity': 0,
                'intelligence': 0,
                'defence': 0,
                'agility': 0
            }
        }
        
        # Convert items to WynnData format
        for item in items:
            wynndata_item = {
                'name': item.get('name', ''),
                'tier': item.get('tier', 'Normal'),
                'type': item.get('type', ''),
                'level': item.get('lvl', 0),
                'slot': item.get('slot', '')
            }
            
            # Add identifications if present
            if 'identifications' in item:
                wynndata_item['identifications'] = item['identifications']
            
            wynndata_build['items'].append(wynndata_item)
        
        return wynndata_build

    def save_build_to_file(self, items: List[Dict[str, Any]], filename: str, 
                          format_type: str = 'json', **kwargs) -> bool:
        """
        Save build to file in specified format
        
        Args:
            items: List of equipped items
            filename: Output filename
            format_type: Export format ('json', 'text', 'wynndata')
            **kwargs: Additional arguments for export functions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if format_type == 'json':
                data = self.export_json(items, **kwargs)
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                    
            elif format_type == 'text':
                data = self.export_text_summary(items, **kwargs)
                with open(filename, 'w') as f:
                    f.write(data)
                    
            elif format_type == 'wynndata':
                data = self.export_wynndata_format(items, **kwargs)
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                    
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
            return True
            
        except Exception as e:
            print(f"Error saving build to file: {e}")
            return False

    def _get_class_number(self, player_class: str) -> int:
        """Convert class name to Wynnbuilder class number"""
        class_numbers = {
            'mage': 0,
            'archer': 1,
            'warrior': 2,
            'assassin': 3,
            'shaman': 4
        }
        return class_numbers.get(player_class.lower(), 0) if player_class else 0

    def generate_build_hash(self, items: List[Dict[str, Any]], player_class: str = None) -> str:
        """
        Generate unique hash for build identification
        
        Args:
            items: List of equipped items
            player_class: Player's class
            
        Returns:
            Build hash string
        """
        import hashlib
        
        # Create consistent string representation
        build_string = f"{player_class or 'unknown'}_"
        
        # Sort items by slot for consistency
        sorted_items = sorted(items, key=lambda x: (x.get('slot', ''), x.get('name', '')))
        
        for item in sorted_items:
            build_string += f"{item.get('name', '')}_{item.get('lvl', 0)}_"
        
        # Generate hash
        return hashlib.md5(build_string.encode()).hexdigest()[:12]

    def compare_builds(self, build1_items: List[Dict[str, Any]], 
                      build2_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare two builds and highlight differences
        
        Args:
            build1_items: First build's items
            build2_items: Second build's items
            
        Returns:
            Comparison results
        """
        comparison = {
            'identical': False,
            'differences': [],
            'build1_only': [],
            'build2_only': [],
            'common_items': []
        }
        
        # Get item names by slot for each build
        build1_slots = {}
        build2_slots = {}
        
        for item in build1_items:
            slot = item.get('slot', 'unknown')
            name = item.get('name', '')
            build1_slots[slot] = name
        
        for item in build2_items:
            slot = item.get('slot', 'unknown')
            name = item.get('name', '')
            build2_slots[slot] = name
        
        # Find differences
        all_slots = set(build1_slots.keys()) | set(build2_slots.keys())
        
        for slot in all_slots:
            item1 = build1_slots.get(slot)
            item2 = build2_slots.get(slot)
            
            if item1 and item2:
                if item1 == item2:
                    comparison['common_items'].append((slot, item1))
                else:
                    comparison['differences'].append((slot, item1, item2))
            elif item1:
                comparison['build1_only'].append((slot, item1))
            elif item2:
                comparison['build2_only'].append((slot, item2))
        
        comparison['identical'] = (
            len(comparison['differences']) == 0 and 
            len(comparison['build1_only']) == 0 and 
            len(comparison['build2_only']) == 0
        )
        
        return comparison