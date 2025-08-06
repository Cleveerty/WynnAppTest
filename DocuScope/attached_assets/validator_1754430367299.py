def calculate_total_stats(build):
    """Calculates the total stats provided by a given build."""
    total_stats = {
        "strength": 0,
        "dexterity": 0,
        "intelligence": 0,
        "agility": 0,
        "defense_skill": 0,
        "spellDamage": 0,
        "meleeDamage": 0,
        "manaRegen": 0,
        "defense": 0
    }
    for item in build:
        if item and 'stats' in item:
            for stat, value in item['stats'].items():
                total_stats[stat] += value
    return total_stats

def meets_stat_requirements(build):
    """Checks if the build meets the stat requirements for all its items.
    This is a simplified check. A real implementation would need to know
    the specific stat requirements for each item type/tier.
    """
    # For now, we'll assume items have their own stat requirements
    # and we need to sum up the build's total stats to meet them.
    # This part needs actual Wynncraft item data to be accurate.
    # For demonstration, we'll just check if any item has a negative stat
    # which might imply a requirement not met, or if a required stat is missing.
    # This is a placeholder and needs to be refined with actual item requirement logic.
    for item in build:
        if item and 'requirements' in item:
            # This is where you'd check if the total stats from the build
            # satisfy the requirements of this specific item.
            # Example: if item['requirements'].get('strength', 0) > total_stats['strength']:
            # return False
            pass # Placeholder for actual requirement checking
    return True

def is_valid_build(build, max_skill_points=200):
    """Validates a build based on total skill points and item stat requirements."""
    total_skill_points = 0
    for item in build:
        if item and 'stats' in item:
            # Assuming skill points are directly related to primary stats
            # This needs to be adjusted based on how Wynncraft calculates SP
            total_skill_points += item['stats'].get('strength', 0)
            total_skill_points += item['stats'].get('dexterity', 0)
            total_skill_points += item['stats'].get('intelligence', 0)
            total_skill_points += item['stats'].get('agility', 0)
            total_skill_points += item['stats'].get('defense_skill', 0)

    if total_skill_points > max_skill_points:
        return False

    if not meets_stat_requirements(build):
        return False

    return True
