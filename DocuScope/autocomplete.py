"""
Interactive autocomplete and fuzzy matching for Wynncraft items
Uses prompt_toolkit for real-time suggestions and rapidfuzz for intelligent matching
"""

from typing import List, Dict, Any, Optional, Tuple
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import CompleteStyle
import rapidfuzz
from rapidfuzz import fuzz
import re

class ItemCompleter(Completer):
    """Custom completer for Wynncraft items with fuzzy matching"""
    
    def __init__(self, items: List[Dict[str, Any]], slot_type: str = ""):
        self.items = items
        self.slot_type = slot_type
        self.item_names = [item.get('name', '') for item in items if item.get('name')]
    
    def get_completions(self, document, complete_event):
        """Generate completions based on fuzzy matching"""
        text = document.text_before_cursor.lower()
        
        if not text:
            # Show top items when no input
            for i, item in enumerate(self.items[:10]):
                name = item.get('name', '')
                level = item.get('lvl', 0)
                tier = item.get('tier', 'Normal')
                yield Completion(
                    name,
                    start_position=0,
                    display=HTML(f'<style color="#00aa00">{name}</style> <style color="#666666">(Lv.{level} {tier})</style>')
                )
            return
        
        # Fuzzy match items
        matches = []
        for item in self.items:
            name = item.get('name', '')
            if not name:
                continue
                
            # Calculate fuzzy match score
            score = fuzz.partial_ratio(text, name.lower())
            if score > 60:  # Threshold for matching
                matches.append((score, item, name))
        
        # Sort by score and return top matches
        matches.sort(reverse=True, key=lambda x: x[0])
        
        for score, item, name in matches[:15]:
            level = item.get('lvl', 0)
            tier = item.get('tier', 'Normal')
            
            # Color code by tier
            tier_colors = {
                'Normal': '#aaaaaa',
                'Unique': '#ffff55',
                'Rare': '#ff55ff',
                'Legendary': '#55ffff',
                'Fabled': '#ff5555',
                'Mythic': '#aa00aa',
                'Set': '#00ff00'
            }
            
            tier_color = tier_colors.get(tier, '#aaaaaa')
            
            yield Completion(
                name,
                start_position=-len(text),
                display=HTML(f'<style color="{tier_color}">{name}</style> <style color="#666666">(Lv.{level} {tier})</style>')
            )

def fuzzy_search_items(query: str, items: List[Dict[str, Any]], limit: int = 10) -> List[Tuple[int, Dict[str, Any]]]:
    """
    Perform fuzzy search on items and return scored results
    
    Args:
        query: Search query
        items: List of item dictionaries
        limit: Maximum number of results
        
    Returns:
        List of (score, item) tuples sorted by score
    """
    if not query.strip():
        return [(100, item) for item in items[:limit]]
    
    matches = []
    query_lower = query.lower()
    
    for item in items:
        name = item.get('name', '')
        if not name:
            continue
        
        # Multiple scoring methods for better matching
        scores = [
            fuzz.partial_ratio(query_lower, name.lower()),
            fuzz.token_sort_ratio(query_lower, name.lower()),
            fuzz.token_set_ratio(query_lower, name.lower())
        ]
        
        # Boost score for exact prefix matches
        if name.lower().startswith(query_lower):
            scores.append(95)
        
        # Boost score for word boundary matches
        if re.search(r'\b' + re.escape(query_lower), name.lower()):
            scores.append(85)
        
        max_score = max(scores)
        if max_score > 50:  # Minimum threshold
            matches.append((max_score, item))
    
    # Sort by score descending
    matches.sort(reverse=True, key=lambda x: x[0])
    return matches[:limit]

def interactive_item_select(items: List[Dict[str, Any]], slot_name: str, class_filter: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Interactive item selection with fuzzy search and autocompletion
    
    Args:
        items: List of available items
        slot_name: Name of the equipment slot (e.g., "Helmet", "Weapon")
        class_filter: Optional class requirement filter
        
    Returns:
        Selected item dictionary or None if cancelled
    """
    # Filter items by class if specified
    if class_filter and slot_name.lower() == "weapon":
        items = [item for item in items if can_use_item(item, class_filter)]
    
    completer = ItemCompleter(items, slot_name.lower())
    
    # Create colored prompt
    slot_color = {
        'weapon': '#ff6600',
        'helmet': '#66ff66',
        'chestplate': '#6666ff',
        'leggings': '#ffff66',
        'boots': '#ff66ff',
        'ring': '#66ffff',
        'bracelet': '#ffaa66',
        'necklace': '#aa66ff'
    }.get(slot_name.lower(), '#ffffff')
    
    prompt_text = HTML(f'<style color="{slot_color}">Select {slot_name}</style>: ')
    
    try:
        while True:
            # Get user input with autocompletion
            user_input = prompt(
                prompt_text,
                completer=completer,
                complete_style=CompleteStyle.MULTI_COLUMN,
                mouse_support=True
            ).strip()
            
            if not user_input:
                print("No item selected. Skipping slot.")
                return None
            
            if user_input.lower() in ['exit', 'quit', 'cancel']:
                return None
            
            # Find exact match first
            exact_matches = [item for item in items if item.get('name', '').lower() == user_input.lower()]
            if exact_matches:
                selected_item = exact_matches[0]
                print_item_selection(selected_item)
                if confirm_selection():
                    return selected_item
                continue
            
            # Fuzzy search for matches
            matches = fuzzy_search_items(user_input, items, 5)
            
            if not matches:
                print(f"No items found matching '{user_input}'. Try a different search term.")
                continue
            
            if len(matches) == 1:
                selected_item = matches[0][1]
                print_item_selection(selected_item)
                if confirm_selection():
                    return selected_item
                continue
            
            # Multiple matches - show options
            print(f"\nFound {len(matches)} matches for '{user_input}':")
            for i, (score, item) in enumerate(matches, 1):
                name = item.get('name', 'Unknown')
                level = item.get('lvl', 0)
                tier = item.get('tier', 'Normal')
                print(f"  {i}. {name} (Lv.{level} {tier})")
            
            try:
                choice = input("\nEnter number to select (or press Enter to search again): ").strip()
                if not choice:
                    continue
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(matches):
                    selected_item = matches[choice_num - 1][1]
                    print_item_selection(selected_item)
                    if confirm_selection():
                        return selected_item
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")
                
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        return None

def print_item_selection(item: Dict[str, Any]):
    """Print detailed information about selected item"""
    name = item.get('name', 'Unknown')
    level = item.get('lvl', 0)
    tier = item.get('tier', 'Normal')
    item_type = item.get('type', 'Unknown')
    
    print(f"\n┌─ Selected Item ─┐")
    print(f"│ Name: {name}")
    print(f"│ Type: {item_type.title()}")
    print(f"│ Level: {level}")
    print(f"│ Tier: {tier}")
    
    # Show requirements if any
    reqs = []
    for stat in ['str', 'dex', 'int', 'def', 'agi']:
        req_key = f'{stat}Req'
        if req_key in item and item[req_key] > 0:
            reqs.append(f"{stat.upper()}: {item[req_key]}")
    
    if reqs:
        print(f"│ Requirements: {', '.join(reqs)}")
    
    print("└─────────────────┘")

def confirm_selection() -> bool:
    """Ask user to confirm their item selection"""
    while True:
        choice = input("Confirm this selection? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")

def can_use_item(item: Dict[str, Any], player_class: str) -> bool:
    """
    Check if a player class can use this item
    
    Args:
        item: Item dictionary
        player_class: Player class (mage, archer, warrior, assassin, shaman)
        
    Returns:
        True if class can use the item
    """
    # Class-specific weapon types
    class_weapons = {
        'mage': ['wand'],
        'archer': ['bow'],
        'warrior': ['spear'],
        'assassin': ['dagger'],
        'shaman': ['relik']
    }
    
    item_type = item.get('type', '').lower()
    
    # Check weapon restrictions
    if item_type in ['wand', 'bow', 'spear', 'dagger', 'relik']:
        allowed_weapons = class_weapons.get(player_class.lower(), [])
        return item_type in allowed_weapons
    
    # Check class requirement
    class_req = item.get('classReq', '').lower()
    if class_req and class_req != player_class.lower():
        return False
    
    return True

def filter_items_by_slot(items: List[Dict[str, Any]], slot_type: str) -> List[Dict[str, Any]]:
    """
    Filter items by equipment slot type
    
    Args:
        items: List of all items
        slot_type: Equipment slot (helmet, chestplate, etc.)
        
    Returns:
        Filtered list of items for the slot
    """
    if slot_type.lower() == 'weapon':
        weapon_types = ['wand', 'bow', 'spear', 'dagger', 'relik']
        return [item for item in items 
                if item.get('type', '').lower() in weapon_types 
                or item.get('category', '').lower() == 'weapon']
    
    if slot_type.lower() == 'ring':
        return [item for item in items 
                if item.get('type', '').lower() == 'ring' 
                or (item.get('category', '').lower() == 'accessory' and item.get('type', '').lower() == 'ring')]
    
    # For armor pieces
    return [item for item in items 
            if item.get('type', '').lower() == slot_type.lower()
            or (item.get('category', '').lower() == 'armor' and item.get('type', '').lower() == slot_type.lower())]

def get_item_display_name(item: Dict[str, Any]) -> str:
    """Get formatted display name for an item"""
    name = item.get('name', 'Unknown')
    level = item.get('lvl', 0)
    tier = item.get('tier', 'Normal')
    return f"{name} (Lv.{level} {tier})"