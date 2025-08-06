
def calculate_spell_damage(base_damage, spell_multiplier, elemental_bonuses):
    """Calculates spell damage."""
    # Simplified spell damage calculation
    total_elemental_bonus = sum(elemental_bonuses.values())
    return base_damage * spell_multiplier * (1 + total_elemental_bonus / 100)

def calculate_ehp(hp, defense_multiplier):
    """Calculates effective HP."""
    return hp * defense_multiplier

def calculate_mana_sustain(mana_regen, mana_steal, hit_rate):
    """Calculates mana sustain."""
    # Simplified mana sustain calculation
    return mana_regen + (mana_steal * hit_rate)
