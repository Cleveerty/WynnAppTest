"""
Legacy CLI interface - simplified version
Maintained for backward compatibility
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import loader, builder, filters, stats
from export import export_to_wynnbuilder

def main():
    """Main CLI function - simplified version."""
    print("Welcome to WynnBuilder CLI!")
    print("Note: For the full experience, run 'python main.py' instead")
    print()
    
    # Load items
    items_data = loader.load_items()
    if not items_data:
        print("Error: Could not load item data!")
        return
    
    items = items_data.get('items', [])
    print(f"Loaded {len(items)} items")
    
    # Simple build generation
    try:
        # Get basic input
        print("\nChoose your class:")
        print("1. Mage  2. Archer  3. Warrior  4. Assassin  5. Shaman")
        class_choice = input("Enter choice (1-5): ").strip()
        
        class_map = {'1': 'mage', '2': 'archer', '3': 'warrior', '4': 'assassin', '5': 'shaman'}
        class_name = class_map.get(class_choice, 'mage')
        
        print(f"\nSelected: {class_name.title()}")
        
        # Simple filters
        no_mythics = input("Exclude mythic items? (y/n): ").lower().startswith('y')
        
        # Generate builds
        print("\nGenerating builds...")
        
        filtered_items = filters.filter_items(items, class_filter=class_name, no_mythics=no_mythics)
        builds = builder.generate_builds(filtered_items, class_name, 'spellspam', ['thunder'], {'min_dps': 0})
        
        if not builds:
            print("No builds found!")
            return
        
        print(f"Found {len(builds)} builds!")
        
        # Show top 3
        for i, build in enumerate(builds[:3], 1):
            print(f"\nBuild #{i}:")
            for slot, item in build.items():
                print(f"  {slot.title()}: {item.get('name', 'Unknown')}")
            
            build_stats = builder.calculate_build_stats(build)
            print(f"  DPS: {build_stats['dps']:.0f}, Mana: {build_stats['mana']:.1f}, EHP: {build_stats['ehp']:.0f}")
        
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
