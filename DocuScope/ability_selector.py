"""
Interactive ability selection system for Wynncraft classes
Integrates with the main CLI to allow players to choose specific abilities
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm, IntPrompt
from rich.panel import Panel
from rich.text import Text

console = Console()


class AbilitySelector:
    """Handles ability selection for different Wynncraft classes"""
    
    def __init__(self):
        self.abilities_data = {}
        self.load_abilities_data()
    
    def load_abilities_data(self):
        """Load ability data for all classes"""
        data_dir = Path("data")
        
        # Class ability files
        class_files = {
            'mage': 'mage_abilities.json',
            'archer': 'archer_abilities.json',
            'warrior': 'warrior_abilities.json',
            'assassin': 'assassin_abilities.json',
            'shaman': 'shaman_abilities.json'
        }
        
        for class_name, filename in class_files.items():
            file_path = data_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.abilities_data[class_name] = json.load(f)
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not load {filename}: {e}[/yellow]")
                    self.abilities_data[class_name] = []
            else:
                # Create default abilities if file doesn't exist
                self.abilities_data[class_name] = self.get_default_abilities(class_name)
    
    def get_default_abilities(self, class_name: str) -> List[Dict[str, str]]:
        """Get default abilities for a class if no file exists"""
        default_abilities = {
            'mage': [
                {"name": "Meteor", "description": "Deals massive fire damage in a large area with auto-aim radius of 2 blocks."},
                {"name": "Heal", "description": "Heals you and nearby players. Base healing scales with your level."},
                {"name": "Teleport", "description": "Instantly teleport forward 8 blocks. Can pass through walls."},
                {"name": "Ice Snake", "description": "Summons a snake of ice that travels forward, dealing water damage and slowing enemies."},
                {"name": "Wand Proficiency", "description": "Improves your Main Attack's damage and range when using a wand."}
            ],
            'archer': [
                {"name": "Arrow Storm", "description": "Fires multiple arrows in a spread pattern for increased damage coverage."},
                {"name": "Escape", "description": "Leap backwards to create distance from enemies."},
                {"name": "Bomb Arrow", "description": "Fires an explosive arrow that deals area damage."},
                {"name": "Arrow Shield", "description": "Creates a protective barrier that blocks incoming projectiles."},
                {"name": "Bow Proficiency", "description": "Improves your Main Attack's damage and range when using a bow."}
            ],
            'warrior': [
                {"name": "Bash", "description": "A powerful melee attack that can knock back enemies."},
                {"name": "Charge", "description": "Rush forward through enemies, dealing damage along the path."},
                {"name": "Uppercut", "description": "Launch enemies into the air with an upward strike."},
                {"name": "War Scream", "description": "Release a battle cry that buffs allies and intimidates enemies."},
                {"name": "Spear Proficiency", "description": "Improves your Main Attack's damage and range when using a spear."}
            ],
            'assassin': [
                {"name": "Spin Attack", "description": "Spin around to damage all nearby enemies."},
                {"name": "Vanish", "description": "Become invisible for a short time and gain speed boost."},
                {"name": "Multihit", "description": "Strike multiple times in rapid succession."},
                {"name": "Smoke Bomb", "description": "Create a smoke cloud that blinds enemies and provides cover."},
                {"name": "Dagger Proficiency", "description": "Improves your Main Attack's damage and range when using a dagger."}
            ],
            'shaman': [
                {"name": "Totem", "description": "Place a totem that provides beneficial effects to nearby allies."},
                {"name": "Haul", "description": "Pull enemies toward you or push them away."},
                {"name": "Aura", "description": "Create an aura that enhances allies within its radius."},
                {"name": "Uproot", "description": "Cause the ground to erupt, damaging and displacing enemies."},
                {"name": "Relik Proficiency", "description": "Improves your Main Attack's damage and range when using a relik."}
            ]
        }
        
        return default_abilities.get(class_name, [])
    
    def display_abilities(self, class_name: str) -> bool:
        """Display available abilities for a class"""
        if class_name not in self.abilities_data:
            console.print(f"[red]No abilities data found for {class_name}[/red]")
            return False
        
        abilities = self.abilities_data[class_name]
        if not abilities:
            console.print(f"[yellow]No abilities available for {class_name}[/yellow]")
            return False
        
        # Create ability table
        table = Table(title=f"{class_name.title()} Abilities")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Ability Name", style="bold yellow", width=20)
        table.add_column("Description", style="green")
        
        for i, ability in enumerate(abilities, 1):
            table.add_row(
                str(i),
                ability['name'],
                ability['description']
            )
        
        console.print(table)
        return True
    
    def select_abilities(self, class_name: str) -> List[Dict[str, str]]:
        """Interactive ability selection for a class"""
        if class_name not in self.abilities_data:
            console.print(f"[red]No abilities available for {class_name}[/red]")
            return []
        
        abilities = self.abilities_data[class_name]
        if not abilities:
            return []
        
        console.print(f"\n[bold cyan]Step 4: Select {class_name.title()} Abilities[/bold cyan]")
        
        # Display abilities
        if not self.display_abilities(class_name):
            return []
        
        selected_abilities = []
        
        while True:
            console.print(f"\n[bold]Current selection:[/bold] {len(selected_abilities)} abilities")
            if selected_abilities:
                for ability in selected_abilities:
                    console.print(f"  • {ability['name']}")
            
            console.print("\n[bold]Options:[/bold]")
            console.print("  1. Add an ability")
            console.print("  2. Remove an ability")
            console.print("  3. Clear all selections")
            console.print("  4. Finish selection")
            
            try:
                choice = IntPrompt.ask("Choose an option", choices=["1", "2", "3", "4"])
                
                if choice == 1:
                    # Add ability
                    if len(selected_abilities) >= 8:  # Reasonable limit
                        console.print("[yellow]Maximum 8 abilities allowed[/yellow]")
                        continue
                    
                    ability_num = IntPrompt.ask(
                        f"Select ability number (1-{len(abilities)})",
                        choices=[str(i) for i in range(1, len(abilities) + 1)]
                    )
                    
                    selected_ability = abilities[ability_num - 1]
                    
                    # Check if already selected
                    if any(a['name'] == selected_ability['name'] for a in selected_abilities):
                        console.print(f"[yellow]{selected_ability['name']} is already selected[/yellow]")
                    else:
                        selected_abilities.append(selected_ability)
                        console.print(f"[green]✓ Added {selected_ability['name']}[/green]")
                
                elif choice == 2:
                    # Remove ability
                    if not selected_abilities:
                        console.print("[yellow]No abilities selected[/yellow]")
                        continue
                    
                    console.print("\nSelected abilities:")
                    for i, ability in enumerate(selected_abilities, 1):
                        console.print(f"  {i}. {ability['name']}")
                    
                    remove_num = IntPrompt.ask(
                        f"Select ability to remove (1-{len(selected_abilities)})",
                        choices=[str(i) for i in range(1, len(selected_abilities) + 1)]
                    )
                    
                    removed = selected_abilities.pop(remove_num - 1)
                    console.print(f"[yellow]✗ Removed {removed['name']}[/yellow]")
                
                elif choice == 3:
                    # Clear all
                    if selected_abilities and Confirm.ask("Clear all selected abilities?"):
                        selected_abilities.clear()
                        console.print("[yellow]✗ Cleared all selections[/yellow]")
                
                elif choice == 4:
                    # Finish
                    if selected_abilities:
                        break
                    elif Confirm.ask("No abilities selected. Continue anyway?"):
                        break
                        
            except KeyboardInterrupt:
                console.print("\n[yellow]Ability selection cancelled[/yellow]")
                break
        
        if selected_abilities:
            # Summary panel
            summary_text = Text()
            summary_text.append(f"Selected {len(selected_abilities)} abilities for {class_name.title()}:\n\n", style="bold")
            
            for ability in selected_abilities:
                summary_text.append(f"• {ability['name']}\n", style="yellow")
                summary_text.append(f"  {ability['description']}\n\n", style="dim")
            
            console.print(Panel(summary_text, title="Ability Selection Summary", border_style="green"))
        
        return selected_abilities
    
    def save_build_abilities(self, abilities: List[Dict[str, str]], class_name: str, build_name: str = None):
        """Save selected abilities as part of a build"""
        build_dir = Path("builds")
        build_dir.mkdir(exist_ok=True)
        
        build_name = build_name or f"{class_name}_build"
        filename = f"{build_name}_abilities.json"
        
        build_data = {
            'class': class_name,
            'build_name': build_name,
            'abilities': abilities,
            'timestamp': str(Path().cwd())  # Simple timestamp
        }
        
        try:
            with open(build_dir / filename, 'w', encoding='utf-8') as f:
                json.dump(build_data, f, indent=2, ensure_ascii=False)
            console.print(f"[green]✓ Saved abilities to builds/{filename}[/green]")
        except Exception as e:
            console.print(f"[red]Error saving abilities: {e}[/red]")


def main():
    """Test the ability selector"""
    selector = AbilitySelector()
    
    # Test with mage
    selected = selector.select_abilities('mage')
    if selected:
        selector.save_build_abilities(selected, 'mage', 'test_build')


if __name__ == "__main__":
    main()