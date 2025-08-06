#!/usr/bin/env python3
"""
Modern Dropdown-Based Wynncraft Item Builder CLI
Uses prompt_toolkit for interactive dropdown menus and selections
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

# Dropdown interface imports
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import radiolist_dialog, checkboxlist_dialog, input_dialog, message_dialog
from prompt_toolkit.styles import Style

# Import existing modules
from core import loader
from ability_selector import AbilitySelector
from ability_extractor import AbilityExtractor
from autocomplete import filter_items_by_slot, can_use_item, get_item_display_name, fuzzy_search_items

console = Console()


class DropdownWynnBuilder:
    """Modern Wynncraft builder with dropdown-based interface"""
    
    def __init__(self):
        self.items = []
        self.ability_selector = AbilitySelector()
        self.ability_extractor = AbilityExtractor()
        self.current_build = {}
        
        # Define styles for dropdown dialogs
        self.dialog_style = Style.from_dict({
            'dialog': 'bg:#4444aa',
            'dialog frame.label': 'bg:#ffffff #000000',
            'dialog.body': 'bg:#000000 #ffffff',
            'dialog shadow': 'bg:#444444',
            'button': 'bg:#ffffff #000000',
            'button.focused': 'bg:#4444aa #ffffff',
            'radio-checked': 'bg:#4444aa #ffffff',
            'radio-unchecked': 'bg:#000000 #ffffff',
        })
        
        # Equipment slots
        self.equipment_slots = [
            'helmet', 'chestplate', 'leggings', 'boots', 
            'weapon', 'ring', 'ring2', 'bracelet', 'necklace'
        ]
        
        # Classes with descriptions
        self.classes = {
            'mage': {
                'name': 'Mage',
                'weapon_type': 'wand',
                'description': 'Versatile spellcaster with powerful ranged attacks and healing abilities'
            },
            'archer': {
                'name': 'Archer', 
                'weapon_type': 'bow',
                'description': 'Long-range fighter with high damage and mobility spells'
            },
            'warrior': {
                'name': 'Warrior',
                'weapon_type': 'spear',
                'description': 'Melee tank with high defense and area damage abilities'
            },
            'assassin': {
                'name': 'Assassin',
                'weapon_type': 'dagger', 
                'description': 'Fast-paced melee fighter with stealth and multi-hit abilities'
            },
            'shaman': {
                'name': 'Shaman',
                'weapon_type': 'relik',
                'description': 'Support caster with totems, healing, and elemental magic'
            }
        }
    
    def load_items(self) -> bool:
        """Load item database with progress indicator"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Loading Wynncraft item database...", total=None)
            
            try:
                data = loader.load_items()
                if data and 'items' in data:
                    self.items = data['items']
                    progress.update(task, description=f"✓ Loaded {len(self.items)} items")
                    return True
                else:
                    progress.update(task, description="✗ No item data found")
                    return False
            except Exception as e:
                progress.update(task, description=f"✗ Failed to load items: {e}")
                return False
    
    def select_class_dropdown(self) -> Optional[str]:
        """Interactive class selection with dropdown"""
        class_choices = []
        for key, info in self.classes.items():
            class_choices.append((key, f"{info['name']} - {info['description']}"))
        
        result = radiolist_dialog(
            title="Select Your Class",
            text="Choose a Wynncraft class for your build:",
            values=class_choices,
            style=self.dialog_style
        ).run()
        
        if result:
            console.print(f"[green]✓ Selected:[/green] [bold cyan]{self.classes[result]['name']}[/bold cyan]")
            console.print(f"[dim]{self.classes[result]['description']}[/dim]")
        
        return result
    
    def select_level_range_dropdown(self) -> Tuple[int, int]:
        """Interactive level range selection"""
        level_ranges = [
            (1, 20, "Early Game (1-20)"),
            (21, 40, "Mid-Early (21-40)"), 
            (41, 60, "Mid Game (41-60)"),
            (61, 80, "Mid-Late (61-80)"),
            (81, 100, "Late Game (81-100)"),
            (101, 106, "End Game (101-106)"),
            (1, 106, "All Levels (1-106)")
        ]
        
        choices = [(f"{min_lvl}-{max_lvl}", desc) for min_lvl, max_lvl, desc in level_ranges]
        
        result = radiolist_dialog(
            title="Select Level Range",
            text="Choose the level range for equipment in your build:",
            values=choices,
            style=self.dialog_style
        ).run()
        
        if result:
            min_lvl, max_lvl = map(int, result.split('-'))
            console.print(f"[green]✓ Level Range:[/green] [cyan]{min_lvl}-{max_lvl}[/cyan]")
            return min_lvl, max_lvl
        
        return 1, 106  # Default
    
    def select_item_from_slot_dropdown(self, slot: str, class_name: str, min_level: int, max_level: int) -> Optional[Dict[str, Any]]:
        """Interactive item selection for a specific slot"""
        console.print(f"\n[bold yellow]Selecting {slot.replace('2', ' 2').title()}[/bold yellow]")
        
        # Filter items for this slot
        if slot == 'weapon':
            weapon_type = self.classes[class_name]['weapon_type']
            slot_items = [item for item in self.items 
                         if item.get('type', '').lower() == weapon_type
                         and min_level <= item.get('lvl', 0) <= max_level]
        elif slot == 'ring2':
            slot_items = filter_items_by_slot(self.items, 'ring')
            slot_items = [item for item in slot_items 
                         if min_level <= item.get('lvl', 0) <= max_level]
        else:
            slot_items = filter_items_by_slot(self.items, slot)
            slot_items = [item for item in slot_items 
                         if min_level <= item.get('lvl', 0) <= max_level]
        
        # Filter by class requirements
        valid_items = [item for item in slot_items if can_use_item(item, class_name)]
        
        if not valid_items:
            message_dialog(
                title="No Items Available",
                text=f"No items found for {slot} slot in level range {min_level}-{max_level}"
            ).run()
            return None
        
        # Sort by level then by tier
        tier_order = {'Mythic': 6, 'Fabled': 5, 'Legendary': 4, 'Rare': 3, 'Unique': 2, 'Set': 1, 'Normal': 0}
        valid_items.sort(key=lambda x: (x.get('lvl', 0), tier_order.get(x.get('tier', 'Normal'), 0)), reverse=True)
        
        # Color-code by tier
        tier_colors = {
            'Mythic': '🟣', 'Fabled': '🟠', 'Legendary': '🟡', 
            'Rare': '🔵', 'Unique': '🟢', 'Set': '🟫', 'Normal': '⚪'
        }
        
        # Create item choices (limit to top 50 for performance)
        item_choices = []
        for item in valid_items[:50]:
            name = item.get('name', 'Unknown')
            level = item.get('lvl', 0)
            tier = item.get('tier', 'Normal')
            icon = tier_colors.get(tier, '⚪')
            
            display_name = f"{icon} {name} (Lv.{level} {tier})"
            item_choices.append((item, display_name))
        
        # Add skip option
        item_choices.append((None, "⏭️  Skip this slot"))
        
        if len(valid_items) > 50:
            # If too many items, use search instead
            search_term = input_dialog(
                title=f"Search {slot.title()} Items",
                text=f"Found {len(valid_items)} items. Enter search term to filter:",
                style=self.dialog_style
            ).run()
            
            if search_term:
                # Use fuzzy search
                matches = fuzzy_search_items(search_term, valid_items, 20)
                item_choices = []
                for score, item in matches:
                    name = item.get('name', 'Unknown')
                    level = item.get('lvl', 0)
                    tier = item.get('tier', 'Normal')
                    icon = tier_colors.get(tier, '⚪')
                    display_name = f"{icon} {name} (Lv.{level} {tier}) - {score}%"
                    item_choices.append((item, display_name))
                
                item_choices.append((None, "⏭️  Skip this slot"))
        
        result = radiolist_dialog(
            title=f"Select {slot.replace('2', ' 2').title()}",
            text=f"Choose an item for your {slot} slot ({len(valid_items)} available):",
            values=item_choices,
            style=self.dialog_style
        ).run()
        
        if result:
            console.print(f"[green]✓ Selected:[/green] {get_item_display_name(result)}")
        else:
            console.print(f"[yellow]⏭️  Skipped {slot} slot[/yellow]")
        
        return result
    
    def select_abilities_dropdown(self, class_name: str) -> List[Dict[str, str]]:
        """Interactive ability selection with checkboxes"""
        # Load the extracted abilities for the class
        abilities_file = Path(f"data/{class_name}_abilities_extracted.json")
        if abilities_file.exists():
            with open(abilities_file, 'r') as f:
                abilities = json.load(f)
        else:
            # Fallback to default abilities
            abilities = self.ability_selector.abilities_data.get(class_name, [])
        
        if not abilities:
            message_dialog(
                title="No Abilities Available",
                text=f"No abilities found for {class_name.title()} class"
            ).run()
            return []
        
        console.print(f"[bold cyan]Found {len(abilities)} abilities for {class_name.title()}[/bold cyan]")
        
        # Create ability choices for checkbox dialog
        ability_choices = []
        for ability in abilities[:30]:  # Limit to first 30 for UI performance
            name = ability.get('name', 'Unknown')
            desc = ability.get('description', '')[:60] + "..." if len(ability.get('description', '')) > 60 else ability.get('description', '')
            display_text = f"{name}: {desc}"
            ability_choices.append((ability, display_text))
        
        selected = checkboxlist_dialog(
            title=f"Select {class_name.title()} Abilities",
            text=f"Choose abilities for your {class_name.title()} build (select multiple):",
            values=ability_choices,
            style=self.dialog_style
        ).run()
        
        if selected:
            console.print(f"[green]✓ Selected {len(selected)} abilities[/green]")
            for ability in selected:
                console.print(f"  • [yellow]{ability['name']}[/yellow]")
        else:
            console.print("[yellow]No abilities selected[/yellow]")
            
        return selected or []
    
    def display_build_summary(self):
        """Display comprehensive build summary"""
        console.print("\n[bold cyan]🏗️  Build Summary[/bold cyan]")
        
        # Equipment table
        if self.current_build.get('items'):
            equipment_table = Table(title="Selected Equipment", show_header=True)
            equipment_table.add_column("Slot", style="cyan", width=12)
            equipment_table.add_column("Item", style="yellow", width=30)
            equipment_table.add_column("Level", style="green", width=8)
            equipment_table.add_column("Tier", style="magenta", width=10)
            
            for slot, item in self.current_build['items'].items():
                display_slot = slot.replace('2', ' 2').title()
                name = item.get('name', 'Unknown')
                level = str(item.get('lvl', 0))
                tier = item.get('tier', 'Normal')
                equipment_table.add_row(display_slot, name, level, tier)
            
            console.print(equipment_table)
        
        # Abilities table
        if self.current_build.get('abilities'):
            abilities_table = Table(title="Selected Abilities", show_header=True)
            abilities_table.add_column("Ability", style="yellow", width=25)
            abilities_table.add_column("Description", style="green")
            
            for ability in self.current_build['abilities']:
                abilities_table.add_row(ability['name'], ability['description'][:80] + "..." if len(ability['description']) > 80 else ability['description'])
            
            console.print(abilities_table)
        
        # Basic stats summary
        total_items = len(self.current_build.get('items', {}))
        total_abilities = len(self.current_build.get('abilities', []))
        
        summary_text = Text()
        summary_text.append(f"Class: {self.classes[self.current_build['class']]['name']}\n", style="bold cyan")
        summary_text.append(f"Equipment Pieces: {total_items}/9\n", style="green" if total_items >= 7 else "yellow")
        summary_text.append(f"Selected Abilities: {total_abilities}\n", style="green" if total_abilities > 0 else "yellow")
        summary_text.append(f"Level Range: {self.current_build.get('level_range', (1, 106))[0]}-{self.current_build.get('level_range', (1, 106))[1]}", style="blue")
        
        console.print(Panel(summary_text, title="Build Overview", border_style="green"))
    
    def run(self):
        """Main application loop with dropdown interface"""
        try:
            console.print("[bold cyan]🎯 Wynncraft Build Generator - Dropdown Edition[/bold cyan]\n")
            
            # Load items
            if not self.load_items():
                console.print("[red]Failed to load item database. Exiting.[/red]")
                return 1
            
            # Class selection
            player_class = self.select_class_dropdown()
            if not player_class:
                console.print("[yellow]No class selected. Exiting.[/yellow]")
                return 0
            
            # Level range
            min_level, max_level = self.select_level_range_dropdown()
            
            # Initialize build
            self.current_build = {
                'class': player_class,
                'level_range': (min_level, max_level),
                'items': {},
                'abilities': []
            }
            
            # Equipment selection
            console.print(f"\n[bold cyan]Building {self.classes[player_class]['name']} Equipment[/bold cyan]")
            
            for slot in self.equipment_slots:
                selected_item = self.select_item_from_slot_dropdown(slot, player_class, min_level, max_level)
                if selected_item:
                    self.current_build['items'][slot] = selected_item
            
            # Ability selection
            selected_abilities = self.select_abilities_dropdown(player_class)
            self.current_build['abilities'] = selected_abilities
            
            # Display final build
            self.display_build_summary()
            
            # Ask if user wants to save/export
            export_choice = radiolist_dialog(
                title="Export Build",
                text="Would you like to export your build?",
                values=[
                    ('json', 'Save as JSON file'),
                    ('text', 'Display as text summary'),
                    ('none', 'No export')
                ],
                style=self.dialog_style
            ).run()
            
            if export_choice == 'json':
                filename = f"build_{player_class}_{min_level}-{max_level}.json"
                with open(filename, 'w') as f:
                    json.dump(self.current_build, f, indent=2)
                console.print(f"[green]✓ Build saved to {filename}[/green]")
            elif export_choice == 'text':
                console.print("\n[bold]Text Summary:[/bold]")
                console.print(f"Class: {self.classes[player_class]['name']}")
                console.print(f"Level Range: {min_level}-{max_level}")
                console.print(f"Equipment: {len(self.current_build['items'])} pieces")
                console.print(f"Abilities: {len(self.current_build['abilities'])} selected")
            
            console.print("\n[bold green]✨ Build complete! Thank you for using WynnBuilder![/bold green]")
            return 0
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Build cancelled by user.[/yellow]")
            return 0
        except Exception as e:
            console.print(f"\n[red]An error occurred: {e}[/red]")
            return 1


if __name__ == "__main__":
    app = DropdownWynnBuilder()
    sys.exit(app.run())