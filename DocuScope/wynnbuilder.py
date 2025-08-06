#!/usr/bin/env python3
"""
WynnBuilder Launcher - Choose Your Interface
Provides access to all WynnBuilder interfaces and tools
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.styles import Style

console = Console()

def main():
    """Main launcher with interface selection"""
    console.print("[bold cyan]🏗️  WynnBuilder - Wynncraft Build Generator[/bold cyan]\n")
    
    # Display welcome message
    welcome_text = Text()
    welcome_text.append("Welcome to WynnBuilder!\n\n", style="bold")
    welcome_text.append("• 4,186 authentic Wynncraft items\n", style="green")
    welcome_text.append("• 92 extracted Mage abilities from official wiki\n", style="green")
    welcome_text.append("• Multiple interface options for different preferences\n", style="green")
    welcome_text.append("• Export compatibility with Wynnbuilder website\n", style="green")
    
    console.print(Panel(welcome_text, title="Features", border_style="blue"))
    
    # Interface selection
    dialog_style = Style.from_dict({
        'dialog': 'bg:#4444aa',
        'dialog frame.label': 'bg:#ffffff #000000',
        'dialog.body': 'bg:#000000 #ffffff',
        'dialog shadow': 'bg:#444444',
        'button': 'bg:#ffffff #000000',
        'button.focused': 'bg:#4444aa #ffffff',
        'radio-checked': 'bg:#4444aa #ffffff',
        'radio-unchecked': 'bg:#000000 #ffffff',
    })
    
    interface_options = [
        ('dropdown', '🎯 Dropdown Interface - Easy point-and-click selections (Recommended)'),
        ('interactive', '⚡ Advanced Interactive CLI - Fuzzy search and autocompletion'),
        ('web', '🌐 Web Interface - Browser-based build generator (runs on port 5000)'),
        ('extract', '📄 Extract Abilities - Process HTML files with ability data'),
        ('quit', '🚪 Exit')
    ]
    
    choice = radiolist_dialog(
        title="Choose Interface",
        text="Select how you'd like to use WynnBuilder:",
        values=interface_options,
        style=dialog_style
    ).run()
    
    if not choice or choice == 'quit':
        console.print("[yellow]Goodbye![/yellow]")
        return 0
    
    try:
        if choice == 'dropdown':
            console.print("[cyan]Starting Dropdown Interface...[/cyan]")
            from dropdown_cli import DropdownWynnBuilder
            app = DropdownWynnBuilder()
            return app.run()
            
        elif choice == 'interactive':
            console.print("[cyan]Starting Interactive CLI...[/cyan]")
            from interactive_cli import InteractiveWynnBuilder
            app = InteractiveWynnBuilder()
            return app.run()
            
        elif choice == 'web':
            console.print("[cyan]Starting Web Interface on http://localhost:5000...[/cyan]")
            console.print("[dim]Press Ctrl+C to stop the server[/dim]")
            from web_interface import start_web_server
            start_web_server()
            return 0
            
        elif choice == 'extract':
            console.print("[cyan]Starting Ability Extractor...[/cyan]")
            from ability_extractor import main
            main()
            return 0
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled.[/yellow]")
        return 0
    except ImportError as e:
        console.print(f"[red]Error importing module: {e}[/red]")
        console.print("[yellow]Some dependencies may be missing.[/yellow]")
        return 1
    except Exception as e:
        console.print(f"[red]An error occurred: {e}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())