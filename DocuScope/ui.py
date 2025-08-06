"""
UI module for the Wynncraft CLI tool using Rich
Handles all visual output and user interaction
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.columns import Columns
from rich.layout import Layout
from rich.align import Align
from rich import box
import os

console = Console()

class WynnCLI:
    """Rich-based CLI interface for Wynncraft build tool."""
    
    def __init__(self):
        self.console = console
    
    def show_welcome(self):
        """Display welcome banner."""
        welcome_text = Text()
        welcome_text.append("🏰 ", style="gold1")
        welcome_text.append("WynnBuilder CLI", style="bold cyan")
        welcome_text.append(" 🏰", style="gold1")
        
        subtitle = Text("Advanced Wynncraft Build Generator with AI Assistant", style="dim")
        
        panel = Panel(
            Align.center(welcome_text + "\n" + subtitle),
            box=box.DOUBLE,
            border_style="cyan",
            padding=(1, 2)
        )
        
        self.console.print("\n")
        self.console.print(panel)
        self.console.print()
    
    def show_main_menu(self):
        """Display main menu options."""
        menu_table = Table(show_header=False, box=box.ROUNDED, border_style="blue")
        menu_table.add_column("Option", style="cyan", width=8)
        menu_table.add_column("Description", style="white")
        
        menu_table.add_row("1", "🔨 Generate Builds")
        menu_table.add_row("2", "🤖 AI Assistant")
        menu_table.add_row("3", "🌐 Web Interface")
        menu_table.add_row("4", "❓ Help")
        menu_table.add_row("5", "🚪 Exit")
        
        panel = Panel(
            menu_table,
            title="[bold blue]Main Menu[/bold blue]",
            border_style="blue"
        )
        
        self.console.print(panel)
    
    def get_build_config(self):
        """Get build configuration from user."""
        try:
            config = {}
            
            # Class selection
            self.console.print("\n[bold cyan]📋 Build Configuration[/bold cyan]")
            
            class_table = Table(show_header=False, box=box.SIMPLE)
            class_table.add_column("ID", style="cyan", width=3)
            class_table.add_column("Class", style="yellow")
            class_table.add_column("Description", style="dim")
            
            classes = [
                ("1", "Mage", "Spell damage specialist"),
                ("2", "Archer", "Ranged damage dealer"), 
                ("3", "Warrior", "Melee tank/damage"),
                ("4", "Assassin", "High DPS melee"),
                ("5", "Shaman", "Support/healing")
            ]
            
            for class_id, name, desc in classes:
                class_table.add_row(class_id, name, desc)
            
            self.console.print(Panel(class_table, title="Classes", border_style="yellow"))
            
            class_choice = Prompt.ask("Choose your class", choices=["1", "2", "3", "4", "5"], default="1")
            class_map = {'1': 'mage', '2': 'archer', '3': 'warrior', '4': 'assassin', '5': 'shaman'}
            config['class'] = class_map[class_choice]
            
            # Playstyle selection
            playstyle_table = Table(show_header=False, box=box.SIMPLE)
            playstyle_table.add_column("ID", style="cyan", width=3)
            playstyle_table.add_column("Style", style="green")
            playstyle_table.add_column("Focus", style="dim")
            
            playstyles = [
                ("1", "Spellspam", "High spell damage & mana"),
                ("2", "Melee", "High melee damage"),
                ("3", "Hybrid", "Balanced spell/melee"),
                ("4", "Tank", "High defense & HP")
            ]
            
            for style_id, name, focus in playstyles:
                playstyle_table.add_row(style_id, name, focus)
            
            self.console.print(Panel(playstyle_table, title="Playstyles", border_style="green"))
            
            playstyle_choice = Prompt.ask("Choose playstyle", choices=["1", "2", "3", "4"], default="1")
            playstyle_map = {'1': 'spellspam', '2': 'melee', '3': 'hybrid', '4': 'tank'}
            config['playstyle'] = playstyle_map[playstyle_choice]
            
            # Element selection
            self.console.print("\n[yellow]🔥 Element Selection[/yellow]")
            elements_input = Prompt.ask("Elements (comma-separated)", default="thunder,water")
            config['elements'] = [e.strip().lower() for e in elements_input.split(',')]
            
            # Filters
            self.console.print("\n[magenta]⚙️  Build Filters[/magenta]")
            config['no_mythics'] = not Confirm.ask("Allow mythic items?", default=True)
            
            min_dps = IntPrompt.ask("Minimum spell DPS", default=0)
            min_mana = IntPrompt.ask("Minimum mana regen", default=0)
            max_cost = IntPrompt.ask("Maximum build cost (emeralds, 0 = no limit)", default=0)
            
            config['filters'] = {
                'min_dps': min_dps,
                'min_mana_regen': min_mana,
                'max_cost': max_cost if max_cost > 0 else None
            }
            
            return config
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Configuration cancelled.[/yellow]")
            return None
    
    def display_builds(self, builds, class_name):
        """Display generated builds in a formatted table."""
        if not builds:
            self.console.print("[red]No builds to display![/red]")
            return
        
        self.console.print(f"\n[bold green]🏆 Top {len(builds)} Builds for {class_name.title()}[/bold green]\n")
        
        for i, build in enumerate(builds, 1):
            # Calculate stats
            from core.builder import calculate_build_stats
            stats = calculate_build_stats(build)
            
            # Create build table
            build_table = Table(box=box.ROUNDED, border_style="green")
            build_table.add_column("Slot", style="cyan", width=12)
            build_table.add_column("Item", style="yellow", width=25)
            build_table.add_column("Type", style="dim", width=10)
            
            # Add items to table
            slot_order = ['weapon', 'helmet', 'chestplate', 'leggings', 'boots', 'ring1', 'ring2', 'bracelet', 'necklace']
            
            for slot in slot_order:
                if slot in build:
                    item = build[slot]
                    item_name = item.get('name', 'Unknown')
                    item_type = item.get('type', '').title()
                    
                    # Color code by rarity
                    tier = item.get('tier', 'Normal')
                    if tier == 'Mythic':
                        item_style = "bold magenta"
                    elif tier == 'Legendary':
                        item_style = "bold yellow"
                    elif tier == 'Rare':
                        item_style = "bold blue"
                    elif tier == 'Unique':
                        item_style = "bold green"
                    else:
                        item_style = "white"
                    
                    build_table.add_row(
                        slot.replace('1', ' 1').replace('2', ' 2').title(),
                        f"[{item_style}]{item_name}[/{item_style}]",
                        item_type
                    )
            
            # Stats table
            stats_table = Table(show_header=False, box=box.SIMPLE, border_style="blue")
            stats_table.add_column("Stat", style="cyan", width=12)
            stats_table.add_column("Value", style="bold white")
            
            stats_table.add_row("💀 DPS", f"{stats['dps']:.0f}")
            stats_table.add_row("🔵 Mana", f"{stats['mana']:.1f}/s")
            stats_table.add_row("❤️  EHP", f"{stats['ehp']:.0f}")
            stats_table.add_row("💰 Cost", f"{stats.get('cost', 0):.0f} EB")
            
            # Combine tables
            layout = Table.grid(padding=1)
            layout.add_column()
            layout.add_column()
            
            layout.add_row(build_table, stats_table)
            
            panel = Panel(
                layout,
                title=f"[bold green]Build #{i}[/bold green]",
                border_style="green"
            )
            
            self.console.print(panel)
    
    def show_help(self):
        """Display help information."""
        help_text = Text()
        help_text.append("🎯 ", style="gold1")
        help_text.append("WynnBuilder CLI Help", style="bold cyan")
        help_text.append("\n\n", style="white")
        
        help_sections = [
            ("Build Generator", "Generate optimized builds based on class, playstyle, and preferences"),
            ("AI Assistant", "Ask natural language questions about builds and get intelligent responses"),
            ("Web Interface", "Access the tool through a web browser interface"),
            ("Filters", "Use filters to narrow down builds (mythics, DPS, mana, cost)"),
            ("Export", "Export builds as Wynnbuilder-compatible strings for sharing")
        ]
        
        help_table = Table(box=box.ROUNDED, border_style="cyan")
        help_table.add_column("Feature", style="bold yellow", width=15)
        help_table.add_column("Description", style="white")
        
        for feature, desc in help_sections:
            help_table.add_row(feature, desc)
        
        formulas_text = Text()
        formulas_text.append("📊 Damage Calculation:\n", style="bold blue")
        formulas_text.append("• Spell damage uses conversion formulas from game mechanics\n", style="dim")
        formulas_text.append("• EHP = HP × defense multipliers\n", style="dim")
        formulas_text.append("• Mana sustain = regen + (steal × hit rate)\n", style="dim")
        formulas_text.append("• Spell costs use INT reduction formula\n", style="dim")
        
        tips_text = Text()
        tips_text.append("💡 Tips:\n", style="bold green")
        tips_text.append("• Use specific elements for better damage focus\n", style="dim")
        tips_text.append("• Higher DPS filters may exclude sustain builds\n", style="dim")
        tips_text.append("• Tank builds prioritize EHP over DPS\n", style="dim")
        tips_text.append("• Mythic items have unique mechanics\n", style="dim")
        
        layout = Layout()
        layout.split_column(
            Layout(Panel(help_table, title="Features", border_style="cyan")),
            Layout(Panel(formulas_text, title="Calculations", border_style="blue")),
            Layout(Panel(tips_text, title="Tips", border_style="green"))
        )
        
        self.console.print(layout)
        self.console.print("\n[dim]Press Enter to continue...[/dim]")
        input()
