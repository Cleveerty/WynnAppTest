
from core import loader, builder, filters, stats
from export import export_to_wynnbuilder

def main():
    """Main function for the Wynncraft Item Builder CLI."""
    print("Welcome to WynnBuilder CLI!")

    # Load items
    items = loader.load_items()
    if not items:
        return

    # Get user input
    class_choice = input("Choose your class: [1] Mage, [2] Archer, [3] Warrior, [4] Assassin, [5] Shaman: ")
    class_map = {'1': 'Mage', '2': 'Archer', '3': 'Warrior', '4': 'Assassin', '5': 'Shaman'}
    class_name = class_map.get(class_choice)

    playstyle = input("Playstyle: [1] Spellspam, [2] Melee, [3] Hybrid, [4] Tank: ")
    elements = input("Elements (comma-separated): ").split(',')
    no_mythics = input("Allow mythics? (y/n): ").lower() == 'n'
    min_dps = int(input("Min spell DPS?: ") or 0)
    min_mana_regen = int(input("Min mana regen?: ") or 0)

    # Generate and evaluate builds
    print("Generating builds...")
    build_filters = {
        'min_dps': min_dps,
        'min_mana_regen': min_mana_regen
    }
    generated_builds = builder.generate_builds(items, class_name, playstyle, elements, build_filters)

    if not generated_builds:
        print("No builds found!")
        return

    print(f"[✓] {len(generated_builds)} builds found!")

    # Sort and display the top builds
    sorted_builds = sorted(generated_builds, key=lambda b: builder.calculate_build_stats(b)['dps'], reverse=True)

    for i, build in enumerate(sorted_builds[:10]):
        build_stats = builder.calculate_build_stats(build)
        print(f"\n# {i + 1} {class_name} Build:")
        for item_type, item in build.items():
            print(f"{item_type.capitalize()}: {item['name']}")
        print(f"DPS: {build_stats['dps']} | Mana: {build_stats['mana']} | EHP: {build_stats['ehp']}")

        export = input("Export this build to Wynnbuilder? (y/n): ").lower() == 'y'
        if export:
            build_list = [class_name] + [item['name'] for item in build.values()]
            export_string = export_to_wynnbuilder(build_list)
            with open(f"build_{i + 1}.txt", "w") as f:
                f.write(export_string)
            print(f"Exported as: build_{i + 1}.txt and wynnbuilder string: {export_string}")

if __name__ == "__main__":
    main()
