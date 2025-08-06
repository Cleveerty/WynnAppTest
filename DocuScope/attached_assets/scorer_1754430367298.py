from core.validator import calculate_total_stats

def score_build(build, custom_scoring_function=None):
    """Scores a build based on its total stats. Customizable with a custom scoring function."""
    total_stats = calculate_total_stats(build)

    if custom_scoring_function:
        try:
            # Execute custom scoring function if provided
            # The custom function should accept a dictionary of total_stats
            score = custom_scoring_function(total_stats)
        except Exception as e:
            print(f"Error executing custom scoring function: {e}")
            # Fallback to default scoring if custom function fails
            score = total_stats.get('spellDamage', 0) + \
                    total_stats.get('meleeDamage', 0) + \
                    total_stats.get('manaRegen', 0) * 10 + \
                    total_stats.get('defense', 0) / 1000
    else:
        # Default scoring function
        # score = damage + mana_regen * 10 + ehp / 1000
        # For simplicity, using defense as a proxy for EHP for now
        score = total_stats.get('spellDamage', 0) + \
                total_stats.get('meleeDamage', 0) + \
                total_stats.get('manaRegen', 0) * 10 + \
                total_stats.get('defense', 0) / 1000

    return score
