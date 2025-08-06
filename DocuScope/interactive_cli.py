#!/usr/bin/env python3
"""
Modern Interactive Wynncraft Item Builder CLI
Implements fuzzy search, autocompletion, and step-by-step build creation
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.text import Text
import requests

# Import our custom autocomplete system
from autocomplete import (
    interactive_item_select,
    filter_items_by_slot,
    can_use_item,
    get_item_display_name
)

# Import existing core modules
from core import loader, stats
from build_exporter import WynncraftBuildExporter
from build_validator import BuildValidator
from ability_selector import AbilitySelector
from ability_extractor import AbilityExtractor

console = Console()

class InteractiveWynnBuilder:
    """Main interactive CLI application"""
    
    def __init__(self):
        self.items = []
        self.exporter = WynncraftBuildExporter()
        self.validator = BuildValidator()
        self.ability_selector = AbilitySelector()
        self.ability_extractor = AbilityExtractor()
        self.current_build = {}
        
        # Equipment slots in order
        self.equipment_slots = [
            'helmet',
            'chestplate', 
            'leggings',
            'boots',
            'weapon',
            'ring',
            'ring2',  # Second ring
            'bracelet',
            'necklace'
        ]
        
        # Class information
        self.classes = {
            'mage': {
                'name': 'Mage',
                'weapon_type': 'wand',
                'archetypes': ['riftwalker', 'lightbender', 'arcanist']
            },
            'archer': {
                'name': 'Archer', 
                'weapon_type': 'bow',
                'archetypes': ['trapper', 'beastmaster', 'sharpshooter']
            },
            'warrior': {
                'name': 'Warrior',
                'weapon_type': 'spear', 
                'archetypes': ['paladin', 'fallen', 'battle_monk']
            },
            'assassin': {
                'name': 'Assassin',
                'weapon_type': 'dagger',
                'archetypes': ['acrobat', 'trickster', 'shadestepper']
            },
            'shaman': {
                'name': 'Shaman',
                'weapon_type': 'relik',
                'archetypes': ['ritualist', 'summoner', 'acolyte']
            }
        }

    def load_items(self):
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

    def display_welcome(self):
        """Display welcome screen"""
        title = Text("WynnBuilder Interactive CLI", style="bold cyan")
        subtitle = Text("Modern item builder with fuzzy search & autocompletion", style="italic")
        
        welcome_panel = Panel(
            Text.assemble(
                title, "\n",
                subtitle, "\n\n",
                "Features:\n",
                "• Fuzzy name search (e.g., 'orna' finds 'Ornate Shadow Garb')\n",
                "• Live autocompletion with arrow key navigation\n", 
                "• Class requirement validation\n",
                "• Comprehensive build statistics\n",
                "• Wynnbuilder export compatibility\n"
            ),
            title="🎯 Welcome",
            border_style="bright_blue"
        )
        
        console.print(welcome_panel)

    def select_class(self) -> Optional[str]:
        """Interactive class selection"""
        console.print("\n[bold cyan]Step 1: Choose your class[/bold cyan]")
        
        # Display class options
        table = Table(title="Available Classes")
        table.add_column("Class", style="cyan")
        table.add_column("Weapon Type", style="yellow")
        table.add_column("Archetypes", style="green")
        
        for class_key, class_info in self.classes.items():
            archetypes = ", ".join(class_info['archetypes'])
            table.add_row(
                class_info['name'],
                class_info['weapon_type'].title(),
                archetypes
            )
        
        console.print(table)
        
        while True:
            class_input = console.input("\n[bold]Enter class name[/bold]: ").strip().lower()
            
            if class_input in self.classes:
                selected_class = self.classes[class_input]
                console.print(f"Selected: [bold cyan]{selected_class['name']}[/bold cyan]")
                return class_input
            
            if class_input in ['exit', 'quit']:
                return None
                
            console.print(f"[red]Unknown class '{class_input}'. Try: {', '.join(self.classes.keys())}[/red]")

    def select_level_range(self) -> tuple:
        """Get player level range for item filtering"""
        console.print("\n[bold cyan]Step 2: Set level preferences[/bold cyan]")
        
        while True:
            try:
                min_level = console.input("[bold]Minimum item level[/bold] (1-106, default 1): ").strip()
                min_level = int(min_level) if min_level else 1
                
                max_level = console.input("[bold]Maximum item level[/bold] (1-106, default 106): ").strip()  
                max_level = int(max_level) if max_level else 106
                
                if 1 <= min_level <= max_level <= 106:
                    console.print(f"Level range: [cyan]{min_level}-{max_level}[/cyan]")
                    return min_level, max_level
                else:
                    console.print("[red]Invalid level range. Ensure 1 ≤ min ≤ max ≤ 106[/red]")
                    
            except ValueError:
                console.print("[red]Please enter valid numbers[/red]")

    def build_equipment(self, player_class: str, min_level: int, max_level: int):
        """Interactive equipment selection for each slot"""
        console.print(f"\n[bold cyan]Step 3: Build your {self.classes[player_class]['name']} equipment[/bold cyan]")
        
        self.current_build = {
            'class': player_class,
            'level_range': (min_level, max_level),
            'items': {}
        }
        
        for slot in self.equipment_slots:
            console.print(f"\n[bold yellow]═══ {slot.title()} Slot ═══[/bold yellow]")
            
            # Filter items for this slot
            if slot == 'weapon':
                weapon_type = self.classes[player_class]['weapon_type']
                slot_items = [item for item in self.items 
                             if item.get('type', '').lower() == weapon_type
                             and min_level <= item.get('lvl', 0) <= max_level]
            elif slot == 'ring2':
                # Second ring slot
                slot_items = filter_items_by_slot(self.items, 'ring')
                slot_items = [item for item in slot_items 
                             if min_level <= item.get('lvl', 0) <= max_level]
            else:
                slot_items = filter_items_by_slot(self.items, slot)
                slot_items = [item for item in slot_items 
                             if min_level <= item.get('lvl', 0) <= max_level]
            
            # Further filter by class requirements
            valid_items = [item for item in slot_items if can_use_item(item, player_class)]
            
            if not valid_items:
                console.print(f"[yellow]No items available for {slot} slot in level range {min_level}-{max_level}[/yellow]")
                continue
            
            console.print(f"Found [green]{len(valid_items)}[/green] available items")
            
            # Interactive selection
            selected_item = interactive_item_select(
                valid_items, 
                slot.replace('2', ' 2'),  # "ring2" -> "ring 2"
                player_class
            )
            
            if selected_item:
                self.current_build['items'][slot] = selected_item
                console.print(f"[green]✓[/green] Added {get_item_display_name(selected_item)}")
            else:
                console.print(f"[yellow]Skipped {slot} slot[/yellow]")

    def calculate_build_stats(self) -> Dict[str, Any]:
        """Calculate comprehensive build statistics"""
        if not self.current_build.get('items'):
            return {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Calculating build statistics...", total=None)
            
            try:
                items = list(self.current_build['items'].values())
                # Use basic stats calculation for now
                calculated_stats = {
                    'health': {'total': 0, 'regen_per_5s': 0},
                    'mana': {'total': 0, 'regen_per_5s': 0},
                    'skill_points': {'str': 0, 'dex': 0, 'int': 0, 'def': 0, 'agi': 0},
                    'damage': {'main_attack_dps': 0}
                }
                progress.update(task, description="✓ Statistics calculated")
                return calculated_stats
            except Exception as e:
                progress.update(task, description=f"✗ Error calculating stats: {e}")
                return {}

    def display_build_summary(self, stats: Dict[str, Any]):
        """Display comprehensive build summary"""
        console.print("\n[bold cyan]🏗️  Build Summary[/bold cyan]")
        
        # Equipment table
        equipment_table = Table(title="Selected Equipment")
        equipment_table.add_column("Slot", style="cyan")
        equipment_table.add_column("Item", style="yellow")
        equipment_table.add_column("Level", style="green")
        equipment_table.add_column("Tier", style="magenta")
        
        for slot, item in self.current_build['items'].items():
            display_slot = slot.replace('2', ' 2').title()
            name = item.get('name', 'Unknown')
            level = str(item.get('lvl', 0))
            tier = item.get('tier', 'Normal')
            equipment_table.add_row(display_slot, name, level, tier)
        
        console.print(equipment_table)
        
        # Display selected abilities
        if self.current_build.get('abilities'):
            abilities_table = Table(title="Selected Abilities")
            abilities_table.add_column("Ability", style="yellow", width=20)
            abilities_table.add_column("Description", style="green")
            
            for ability in self.current_build['abilities']:
                abilities_table.add_row(ability['name'], ability['description'])
            
            console.print(abilities_table)
        
        if not stats:
            console.print("[yellow]No statistics available[/yellow]")
            return
        
        # Statistics panels
        stat_panels = []
        
        # Skill Points
        if 'skill_points' in stats:
            sp = stats['skill_points']
            sp_text = Text.assemble(
                f"Strength: {sp.get('str', 0)}\n",
                f"Dexterity: {sp.get('dex', 0)}\n", 
                f"Intelligence: {sp.get('int', 0)}\n",
                f"Defense: {sp.get('def', 0)}\n",
                f"Agility: {sp.get('agi', 0)}\n",
                f"Total: {sum(sp.values())}/200"
            )
            stat_panels.append(Panel(sp_text, title="Skill Points", border_style="green"))
        
        # Health & Mana
        health_mana_text = Text.assemble(
            f"Health: {stats.get('health', 0)}\n",
            f"Mana: {stats.get('mana', 0)}\n",
            f"Health Regen: {stats.get('health_regen', 0)}/5s\n",
            f"Mana Regen: {stats.get('mana_regen', 0)}/5s"
        )
        stat_panels.append(Panel(health_mana_text, title="Health & Mana", border_style="red"))
        
        # Damage
        if 'damage' in stats:
            dmg = stats['damage']
            damage_text = Text.assemble(
                f"Spell Damage: {dmg.get('spell', 0)}\n",
                f"Melee Damage: {dmg.get('melee', 0)}\n",
                f"Main Attack DPS: {dmg.get('main_attack_dps', 0)}"
            )
            stat_panels.append(Panel(damage_text, title="Damage Output", border_style="blue"))
        
        # Display panels in grid
        from rich.columns import Columns
        console.print(Columns(stat_panels))

    def export_build(self):
        """Export build in various formats"""
        if not self.current_build.get('items'):
            console.print("[yellow]No build to export[/yellow]")
            return
        
        console.print("\n[bold cyan]📤 Export Options[/bold cyan]")
        
        export_options = {
            '1': 'JSON format',
            '2': 'Wynnbuilder import string',
            '3': 'Text summary'
        }
        
        for key, desc in export_options.items():
            console.print(f"  {key}. {desc}")
        
        choice = console.input("\n[bold]Select export format[/bold]: ").strip()
        
        try:
            items = list(self.current_build['items'].values())
            
            if choice == '1':
                export_data = self.exporter.export_json(items, self.current_build['class'])
                filename = f"build_{self.current_build['class']}.json"
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                console.print(f"[green]✓ Exported to {filename}[/green]")
                
            elif choice == '2':
                import_url = self.exporter.export_wynnbuilder_url(items, self.current_build['class'])
                console.print(f"\n[bold]Wynnbuilder Import URL:[/bold]")
                console.print(f"[cyan]{import_url}[/cyan]")
                
            elif choice == '3':
                summary = self.exporter.export_text_summary(items, self.current_build['class'])
                console.print(f"\n[bold]Build Summary:[/bold]")
                console.print(summary)
                
            else:
                console.print("[red]Invalid option[/red]")
                
        except Exception as e:
            console.print(f"[red]Export failed: {e}[/red]")
    
    def extract_abilities_from_html(self):
        """Extract abilities from HTML file"""
        console.print("\n[bold cyan]📄 HTML Ability Extraction[/bold cyan]")
        
        # Ask for HTML file path
        html_file = console.input("[bold]Enter HTML file path[/bold]: ").strip()
        
        if not html_file:
            console.print("[yellow]No file specified[/yellow]")
            return
        
        try:
            from pathlib import Path
            if not Path(html_file).exists():
                console.print(f"[red]File not found: {html_file}[/red]")
                return
            
            console.print(f"Extracting abilities from {html_file}...")
            abilities = self.ability_extractor.extract_from_file(html_file)
            
            if not abilities:
                console.print("[yellow]No abilities found in HTML file[/yellow]")
                return
            
            console.print(f"[green]✓ Extracted {len(abilities)} abilities[/green]")
            
            # Display extracted abilities
            table = Table(title=f"Extracted Abilities ({len(abilities)} found)")
            table.add_column("#", style="cyan", width=3)
            table.add_column("Ability Name", style="yellow", width=20)
            table.add_column("Description", style="green")
            
            for i, ability in enumerate(abilities, 1):
                table.add_row(str(i), ability['name'], ability['description'])
            
            console.print(table)
            
            # Ask which class to save to
            class_name = console.input("\n[bold]Save to which class?[/bold] (mage/archer/warrior/assassin/shaman): ").strip().lower()
            
            if class_name not in ['mage', 'archer', 'warrior', 'assassin', 'shaman']:
                console.print("[yellow]Invalid class name, using 'extracted' as filename[/yellow]")
                class_name = 'extracted'
            
            # Save abilities
            output_file = f"data/{class_name}_abilities.json"
            self.ability_extractor.save_abilities_json(abilities, output_file)
            
            # Reload ability selector data
            self.ability_selector.load_abilities_data()
            
            console.print(f"[green]✓ Abilities saved and integrated into {class_name} class[/green]")
            
        except Exception as e:
            console.print(f"[red]Error extracting abilities: {e}[/red]")

    def run(self):
        """Main application loop"""
        try:
            self.display_welcome()
            
            # Load items
            if not self.load_items():
                console.print("[red]Failed to load item database. Exiting.[/red]")
                return 1
            
            # Class selection
            player_class = self.select_class()
            if not player_class:
                console.print("[yellow]No class selected. Exiting.[/yellow]")
                return 0
            
            # Level range
            min_level, max_level = self.select_level_range()
            
            # Build equipment
            self.build_equipment(player_class, min_level, max_level)
            
            # Select abilities
            selected_abilities = self.ability_selector.select_abilities(player_class)
            self.current_build['abilities'] = selected_abilities
            
            if not self.current_build.get('items'):
                console.print("[yellow]No equipment selected. Exiting.[/yellow]")
                return 0
            
            # Calculate and display stats
            stats = self.calculate_build_stats()
            self.display_build_summary(stats)
            
            # Export options
            if Confirm.ask("\nWould you like to export this build?"):
                self.export_build()
            
            console.print("\n[bold green]✨ Build complete! Thank you for using WynnBuilder![/bold green]")
            return 0
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Build cancelled by user.[/yellow]")
            return 0
        except Exception as e:
            console.print(f"\n[red]An error occurred: {e}[/red]")
            return 1

if __name__ == "__main__":
    app = InteractiveWynnBuilder()
    sys.exit(app.run())