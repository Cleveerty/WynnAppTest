from rich.console import Console
from rich.table import Table

def display_builds(builds):
    """Displays a list of builds in a user-friendly table format."""
    console = Console()

    if not builds:
        console.print("[bold red]No builds found matching your criteria.[/bold red]")
        return

    for i, build_data in enumerate(builds):
        build = build_data['build']
        score = build_data['score']

        console.print(f"\n[bold green]Build {i+1} (Score: {score:.2f})[/bold green]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Slot", style="dim", width=12)
        table.add_column("Item Name")
        table.add_column("Level")
        table.add_column("Stats (Partial)")

        # Group items by type for display
        items_by_slot = {
            "helmet": None,
            "chestplate": None,
            "leggings": None,
            "boots": None,
            "weapon": None,
            "accessory1": None,
            "accessory2": None,
            "accessory3": None,
        }

        accessory_count = 0
        for item in build:
            if item:
                if item['type'] == 'accessory':
                    accessory_count += 1
                    items_by_slot[f'accessory{accessory_count}'] = item
                else:
                    items_by_slot[item['type']] = item

        for slot, item in items_by_slot.items():
            if item:
                stats_str = ", ".join([f"{k}: {v}" for k, v in item['stats'].items() if v != 0])
                table.add_row(slot.capitalize(), item['name'], str(item['level']), stats_str)
            else:
                table.add_row(slot.capitalize(), "-", "-", "-")
        
        console.print(table)

def export_build_as_json(builds, filename="wynncraft_builds.json"):
    """Exports the generated builds to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(builds, f, indent=4)
        print(f"Builds successfully exported to {filename}")
    except IOError as e:
        print(f"Error exporting builds to JSON: {e}")
