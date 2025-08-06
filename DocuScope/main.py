#!/usr/bin/env python3
"""
Wynncraft Item Builder CLI Tool
Main entry point for the application
"""

import sys
import os
import json
import requests
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import threading
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import loader, builder, filters, stats
from export import export_to_wynnbuilder
from ui import WynnCLI
from ai_agent import WynnAI
from web_interface import start_web_server

console = Console()

def download_item_data():
    """Download item data from Wynnbuilder GitHub if not present."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    items_file = data_dir / "items.json"
    
    if not items_file.exists():
        console.print("[yellow]Downloading item data from Wynnbuilder...[/yellow]")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Fetching items.json...", total=None)
                
                url = "https://raw.githubusercontent.com/wynnbuilder/wynnbuilder.github.io/master/clean.json"
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Parse and validate JSON
                data = response.json()
                
                # Save to file
                with open(items_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                progress.update(task, completed=True)
                
            console.print(f"[green]✓[/green] Downloaded {len(data.get('items', []))} items")
            
        except Exception as e:
            console.print(f"[red]Error downloading item data: {e}[/red]")
            console.print("[yellow]Please manually download items.json from:[/yellow]")
            console.print("https://raw.githubusercontent.com/wynnbuilder/wynnbuilder.github.io/master/clean.json")
            console.print(f"[yellow]Save it to: {items_file}[/yellow]")
            return False
    
    return True

def main_cli():
    """Main CLI interface."""
    ui = WynnCLI()
    ai = WynnAI()
    
    ui.show_welcome()
    
    # Download data if needed
    if not download_item_data():
        console.print("[red]Cannot proceed without item data.[/red]")
        return
    
    # Load items
    console.print("[cyan]Loading item database...[/cyan]")
    items_data = loader.load_items()
    if not items_data:
        console.print("[red]Failed to load item data![/red]")
        return
    
    items = items_data.get('items', [])
    console.print(f"[green]✓[/green] Loaded {len(items)} items")
    
    while True:
        ui.show_main_menu()
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"], default="1")
        
        if choice == "1":
            # Build generator
            build_interactive(items, ui, ai)
        elif choice == "2":
            # AI assistant
            ai_assistant_mode(ai, items)
        elif choice == "3":
            # Web interface
            start_web_interface()
        elif choice == "4":
            # Help
            ui.show_help()
        elif choice == "5":
            # Exit
            console.print("[green]Thanks for using WynnBuilder CLI![/green]")
            break

def build_interactive(items, ui, ai):
    """Interactive build generation."""
    try:
        # Get user preferences
        config = ui.get_build_config()
        
        if not config:
            return
        
        # Generate builds
        console.print("\n[cyan]Generating builds...[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Calculating combinations...", total=None)
            
            # Filter items first
            filtered_items = filters.filter_items(
                items, 
                class_filter=config['class'],
                playstyle_filter=config['playstyle'],
                no_mythics=config.get('no_mythics', False)
            )
            
            # Generate builds
            builds = builder.generate_builds(
                filtered_items, 
                config['class'], 
                config['playstyle'], 
                config['elements'], 
                config['filters']
            )
            
            progress.update(task, completed=True)
        
        if not builds:
            console.print("[red]No builds found matching your criteria![/red]")
            
            # AI suggestion
            suggestion = ai.suggest_build_alternatives(config)
            if suggestion:
                console.print(f"\n[yellow]AI Suggestion:[/yellow] {suggestion}")
            return
        
        console.print(f"[green]✓[/green] Found {len(builds)} valid builds!")
        
        # Display top builds
        ui.display_builds(builds[:10], config['class'])
        
        # Export options
        if builds and Confirm.ask("\nExport builds?"):
            export_builds(builds[:5], config['class'])
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Build generation cancelled.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error generating builds: {e}[/red]")

def ai_assistant_mode(ai, items):
    """AI assistant mode for natural language queries."""
    console.print("\n[bold cyan]🤖 AI Assistant Mode[/bold cyan]")
    console.print("Ask me anything about Wynncraft builds! Type 'exit' to return to main menu.\n")
    
    while True:
        query = Prompt.ask("[green]You[/green]")
        
        if query.lower() in ['exit', 'quit', 'back']:
            break
        
        try:
            response = ai.process_query(query, items)
            console.print(f"[blue]AI[/blue]: {response}\n")
        except Exception as e:
            console.print(f"[red]AI Error: {e}[/red]\n")

def start_web_interface():
    """Start the web interface in a separate thread."""
    console.print("[cyan]Starting web interface...[/cyan]")
    
    def run_server():
        start_web_server()
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    console.print("[green]✓[/green] Web interface started at http://localhost:5000")
    console.print("Press Enter to return to CLI...")
    input()

def export_builds(builds, class_name):
    """Export builds to files."""
    for i, build in enumerate(builds):
        try:
            # Create build list for export
            build_list = [class_name] + [item['name'] for item in build.values()]
            export_string = export_to_wynnbuilder(build_list)
            
            # Save to file
            filename = f"build_{i + 1}.txt"
            with open(filename, "w") as f:
                f.write(f"Build {i + 1}:\n")
                f.write(f"Class: {class_name}\n")
                f.write(f"Export String: {export_string}\n\n")
                
                # Add item details
                for slot, item in build.items():
                    f.write(f"{slot.capitalize()}: {item['name']}\n")
                
                # Add stats
                build_stats = builder.calculate_build_stats(build)
                f.write(f"\nStats:\n")
                f.write(f"DPS: {build_stats['dps']:.0f}\n")
                f.write(f"Mana: {build_stats['mana']:.1f}\n")
                f.write(f"EHP: {build_stats['ehp']:.0f}\n")
            
            console.print(f"[green]✓[/green] Exported {filename}")
            
        except Exception as e:
            console.print(f"[red]Error exporting build {i + 1}: {e}[/red]")

if __name__ == "__main__":
    try:
        # Check if we should run in web mode (default for deployment)
        mode = os.getenv('WYNN_MODE', 'web')
        
        if mode == 'web':
            # Web server mode
            console.print("[cyan]Starting WynnBuilder in web server mode...[/cyan]")
            
            # Download data if needed
            if not download_item_data():
                console.print("[red]Cannot proceed without item data.[/red]")
                sys.exit(1)
            
            # Test loading items
            console.print("[cyan]Loading item database...[/cyan]")
            items_data = loader.load_items()
            if not items_data:
                console.print("[red]Failed to load item data![/red]")
                sys.exit(1)
            
            items = items_data.get('items', [])
            console.print(f"[green]✓[/green] Loaded {len(items)} items")
            
            # Start web server
            start_web_server()
        else:
            # CLI mode
            main_cli()
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)
