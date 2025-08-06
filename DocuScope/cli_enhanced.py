#!/usr/bin/env python3
"""
Enhanced CLI interface for Wynncraft Item Builder
Implements the improved CLI specification while maintaining web functionality
"""

import argparse
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
import json
from typing import List, Dict, Any, Optional

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import loader, builder, filters, stats
from export import export_to_wynnbuilder, export_build_to_text

console = Console()

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="WynnBuilder CLI - Generate optimized Wynncraft builds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_enhanced.py --class mage --playstyle spellspam --top 5
  python cli_enhanced.py --max-level 105 --element thunder --export builds.json
  python cli_enhanced.py --interactive
        """
    )
    
    # Class selection
    parser.add_argument(
        "--class", 
        dest="player_class",
        choices=["mage", "archer", "warrior", "assassin", "shaman"],
        help="Filter builds by class"
    )
    
    # Level filtering
    parser.add_argument(
        "--max-level",
        type=int,
        default=106,
        help="Maximum item level (default: 106)"
    )
    
    # Playstyle filtering
    parser.add_argument(
        "--playstyle",
        choices=["spellspam", "melee", "hybrid", "tank"],
        help="Filter by playstyle"
    )
    
    # Subclass/Archetype filtering
    parser.add_argument(
        "--archetype",
        choices=["riftwalker", "lightbender", "arcanist"],
        help="Mage archetype (riftwalker, lightbender, arcanist)"
    )
    
    # Element preference
    parser.add_argument(
        "--element",
        choices=["thunder", "water", "earth", "fire", "air"],
        help="Preferred element for builds"
    )
    
    # Build limits
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top builds to display (default: 10)"
    )
    
    # Skill point limit
    parser.add_argument(
        "--max-sp",
        type=int,
        default=200,
        help="Maximum skill points (default: 200)"
    )
    
    # Filters
    parser.add_argument(
        "--no-mythics",
        action="store_true",
        help="Exclude mythic items from builds"
    )
    
    parser.add_argument(
        "--min-dps",
        type=float,
        default=0,
        help="Minimum DPS requirement"
    )
    
    parser.add_argument(
        "--min-mana",
        type=float,
        default=0,
        help="Minimum mana regeneration requirement"
    )
    
    # Export options
    parser.add_argument(
        "--export",
        type=str,
        help="Export builds to JSON file"
    )
    
    parser.add_argument(
        "--export-wynnbuilder",
        action="store_true",
        help="Export builds as Wynnbuilder-compatible strings"
    )
    
    # Interactive mode
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    # Custom scoring
    parser.add_argument(
        "--scoring-formula",
        type=str,
        help="Custom scoring formula (advanced users)"
    )
    
    return parser.parse_args()

def interactive_mode(items: List[Dict[str, Any]]):
    """Interactive CLI mode for build generation."""
    console.print(Panel.fit(
        "[bold cyan]WynnBuilder Interactive Mode[/bold cyan]\n"
        "Configure your build preferences step by step",
        border_style="cyan"
    ))
    
    # Get user preferences
    console.print("\n[bold]Step 1: Choose your class[/bold]")
    class_choice = Prompt.ask(
        "Class",
        choices=["mage", "archer", "warrior", "assassin", "shaman"],
        default="mage"
    )
    
    console.print("\n[bold]Step 2: Choose your playstyle[/bold]")
    playstyle = Prompt.ask(
        "Playstyle",
        choices=["spellspam", "melee", "hybrid", "tank"],
        default="spellspam"
    )
    
    # Add archetype selection for mage
    archetype = None
    if class_choice == "mage":
        console.print("\n[bold]Step 2.1: Choose your mage archetype[/bold]")
        archetype = Prompt.ask(
            "Archetype",
            choices=["riftwalker", "lightbender", "arcanist", "none"],
            default="none"
        )
    
    console.print("\n[bold]Step 3: Set preferences[/bold]")
    max_level = IntPrompt.ask("Maximum item level", default=106)
    max_sp = IntPrompt.ask("Maximum skill points", default=200)
    top_n = IntPrompt.ask("Number of builds to show", default=10)
    
    elements_input = Prompt.ask(
        "Preferred elements (comma-separated)",
        default="thunder,water"
    )
    elements = [e.strip() for e in elements_input.split(",")]
    
    no_mythics = Confirm.ask("Exclude mythic items?", default=False)
    
    # Generate builds
    config = {
        'class': class_choice,
        'playstyle': playstyle,
        'archetype': archetype if archetype != "none" else None,
        'max_level': max_level,
        'max_sp': max_sp,
        'elements': elements,
        'no_mythics': no_mythics,
        'top_n': top_n
    }
    
    generate_and_display_builds(items, config)

def load_ability_trees() -> Dict[str, Any]:
    """Load ability tree data for enhanced calculations."""
    try:
        with open('data/ability_trees.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        console.print("[yellow]Warning: Ability tree data not found, using basic calculations[/yellow]")
        return {}

def generate_and_display_builds(items: List[Dict[str, Any]], config: Dict[str, Any]):
    """Generate and display builds based on configuration."""
    archetype_text = f" ({config['archetype']})" if config.get('archetype') else ""
    console.print(f"\n[cyan]Generating builds for {config['class']} ({config['playstyle']}){archetype_text}...[/cyan]")
    
    # Prepare filters
    build_filters = {
        'max_level': config.get('max_level', 106),
        'max_sp': config.get('max_sp', 200),
        'no_mythics': config.get('no_mythics', False),
        'min_dps': config.get('min_dps', 0),
        'min_mana_regen': config.get('min_mana', 0)
    }
    
    # Filter items
    filtered_items = filters.filter_items(
        items,
        class_filter=config['class'],
        playstyle_filter=config['playstyle'],
        no_mythics=config.get('no_mythics', False)
    )
    
    if not filtered_items:
        console.print("[red]No items found matching your criteria![/red]")
        return
    
    console.print(f"[green]Found {len(filtered_items)} matching items[/green]")
    
    # Generate builds
    builds = builder.generate_builds(
        filtered_items,
        config['class'],
        config['playstyle'],
        config.get('elements', ['thunder']),
        build_filters,
        max_builds=config.get('top_n', 10)
    )
    
    if not builds:
        console.print("[red]No valid builds found![/red]")
        return
    
    # Display builds
    display_builds_table(builds, config['class'])

def display_builds_table(builds: List[Dict[str, Any]], class_name: str):
    """Display builds in a formatted table."""
    console.print(f"\n[bold green]Top {len(builds)} Builds for {class_name.title()}[/bold green]")
    
    for i, build in enumerate(builds, 1):
        # Calculate stats
        build_stats = builder.calculate_build_stats(build)
        
        # Create build table
        table = Table(
            title=f"Build #{i} - Score: {calculate_build_score(build):.1f}",
            show_header=True,
            header_style="bold magenta",
            border_style="blue"
        )
        
        table.add_column("Slot", style="cyan", width=12)
        table.add_column("Item", style="white", width=25)
        table.add_column("Level", style="yellow", width=6)
        table.add_column("Tier", style="green", width=10)
        
        # Add equipment rows
        slots = ['weapon', 'helmet', 'chestplate', 'leggings', 'boots', 'ring1', 'ring2', 'bracelet', 'necklace']
        for slot in slots:
            if slot in build and build[slot]:
                item = build[slot]
                table.add_row(
                    slot.capitalize(),
                    item.get('name', 'Unknown')[:24],
                    str(item.get('lvl', 0)),
                    item.get('tier', 'Normal')
                )
            else:
                table.add_row(slot.capitalize(), "-", "-", "-")
        
        console.print(table)
        
        # Stats table
        stats_table = Table(
            title="Build Statistics",
            show_header=True,
            header_style="bold cyan",
            border_style="green"
        )
        
        stats_table.add_column("Stat", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("DPS", f"{build_stats.get('dps', 0):.1f}")
        stats_table.add_row("Mana/s", f"{build_stats.get('mana', 0):.2f}")
        stats_table.add_row("EHP", f"{build_stats.get('ehp', 0):,.0f}")
        stats_table.add_row("Total SP", f"{build_stats.get('total_sp', 0)}")
        
        # Skill points breakdown
        sp = build_stats.get('skill_points', {})
        stats_table.add_row("STR", str(sp.get('str', 0)))
        stats_table.add_row("DEX", str(sp.get('dex', 0)))
        stats_table.add_row("INT", str(sp.get('int', 0)))
        stats_table.add_row("DEF", str(sp.get('def', 0)))
        stats_table.add_row("AGI", str(sp.get('agi', 0)))
        
        console.print(stats_table)
        console.print()

def calculate_build_score(build: Dict[str, Any]) -> float:
    """Calculate build score using the specified formula."""
    build_stats = builder.calculate_build_stats(build)
    
    # Default scoring: damage + mana_regen * 10 + ehp / 1000
    dps = build_stats.get('dps', 0)
    mana = build_stats.get('mana', 0)
    ehp = build_stats.get('ehp', 0)
    
    score = dps + (mana * 10) + (ehp / 1000)
    return score

def export_builds_to_file(builds: List[Dict[str, Any]], filename: str, class_name: str):
    """Export builds to JSON file."""
    export_data = []
    
    for i, build in enumerate(builds, 1):
        build_stats = builder.calculate_build_stats(build)
        
        export_build = {
            'id': i,
            'class': class_name,
            'score': calculate_build_score(build),
            'items': {},
            'stats': build_stats
        }
        
        # Add items
        slots = ['weapon', 'helmet', 'chestplate', 'leggings', 'boots', 'ring1', 'ring2', 'bracelet', 'necklace']
        for slot in slots:
            if slot in build and build[slot]:
                item = build[slot]
                export_build['items'][slot] = {
                    'name': item.get('name', ''),
                    'level': item.get('lvl', 0),
                    'tier': item.get('tier', 'Normal'),
                    'type': item.get('type', '')
                }
        
        export_data.append(export_build)
    
    try:
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        console.print(f"[green]✓ Exported {len(builds)} builds to {filename}[/green]")
    except Exception as e:
        console.print(f"[red]Error exporting builds: {e}[/red]")

def export_wynnbuilder_strings(builds: List[Dict[str, Any]], class_name: str):
    """Export builds as Wynnbuilder-compatible strings."""
    console.print(f"\n[bold cyan]Wynnbuilder Export Strings for {class_name.title()}[/bold cyan]")
    
    for i, build in enumerate(builds, 1):
        # Create build list for export
        build_list = [class_name.title()]
        
        slots = ['weapon', 'helmet', 'chestplate', 'leggings', 'boots', 'ring1', 'ring2', 'bracelet', 'necklace']
        for slot in slots:
            if slot in build and build[slot]:
                build_list.append(build[slot].get('name', ''))
            else:
                build_list.append('')
        
        try:
            export_string = export_to_wynnbuilder(build_list)
            console.print(f"[green]Build #{i}:[/green] {export_string}")
        except Exception as e:
            console.print(f"[red]Error exporting build #{i}: {e}[/red]")

def main():
    """Main CLI entry point."""
    args = parse_arguments()
    
    # Load items
    console.print("[cyan]Loading Wynncraft item database...[/cyan]")
    items_data = loader.load_items()
    if not items_data:
        console.print("[red]Failed to load item data![/red]")
        sys.exit(1)
    
    items = items_data.get('items', [])
    console.print(f"[green]✓ Loaded {len(items)} items[/green]")
    
    # Run interactive mode if requested
    if args.interactive:
        interactive_mode(items)
        return
    
    # Build configuration from arguments
    config = {
        'class': args.player_class or 'mage',
        'playstyle': args.playstyle or 'spellspam',
        'archetype': getattr(args, 'archetype', None),
        'max_level': args.max_level,
        'max_sp': args.max_sp,
        'elements': [args.element] if args.element else ['thunder'],
        'no_mythics': args.no_mythics,
        'min_dps': args.min_dps,
        'min_mana': args.min_mana,
        'top_n': args.top
    }
    
    # Generate and display builds
    generate_and_display_builds(items, config)
    
    # Handle exports
    if args.export:
        builds = builder.generate_builds(
            filters.filter_items(items, class_filter=config['class'], playstyle_filter=config['playstyle']),
            config['class'],
            config['playstyle'],
            config['elements'],
            {'max_sp': config['max_sp'], 'no_mythics': config['no_mythics']},
            max_builds=config['top_n']
        )
        export_builds_to_file(builds, args.export, config['class'])
    
    if args.export_wynnbuilder:
        builds = builder.generate_builds(
            filters.filter_items(items, class_filter=config['class'], playstyle_filter=config['playstyle']),
            config['class'],
            config['playstyle'],
            config['elements'],
            {'max_sp': config['max_sp'], 'no_mythics': config['no_mythics']},
            max_builds=config['top_n']
        )
        export_wynnbuilder_strings(builds, config['class'])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)