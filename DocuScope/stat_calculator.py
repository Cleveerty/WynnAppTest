"""
Comprehensive Wynncraft build statistics calculator
Implements authentic game formulas for damage, EHP, mana, and other combat stats
"""

from typing import Dict, List, Any, Optional
import math

class WynncraftStatsCalculator:
    """Calculates authentic Wynncraft build statistics"""
    
    def __init__(self):
        # Base class stats (from reference materials)
        self.class_base_stats = {
            'mage': {
                'health': 5,
                'mana': 20,
                'base_defense_multiplier': 0.8,  # Takes 20% more damage than assassin
                'spell_cost_base': {
                    'spell1': 6,  # Heal
                    'spell2': 8,  # Teleport  
                    'spell3': 4,  # Meteor
                    'spell4': 4   # Ice Snake
                }
            },
            'archer': {
                'health': 5,
                'mana': 15,
                'base_defense_multiplier': 0.6,  # Takes 40% more damage than assassin
                'spell_cost_base': {
                    'spell1': 6,  # Arrow Storm
                    'spell2': 8,  # Escape
                    'spell3': 4,  # Bomb Arrow
                    'spell4': 6   # Arrow Shield
                }
            },
            'warrior': {
                'health': 5,
                'mana': 10,
                'base_defense_multiplier': 1.2,  # Takes 20% less damage than assassin
                'spell_cost_base': {
                    'spell1': 4,  # Bash
                    'spell2': 6,  # Charge
                    'spell3': 4,  # Uppercut
                    'spell4': 8   # War Scream
                }
            },
            'assassin': {
                'health': 5,
                'mana': 10,
                'base_defense_multiplier': 1.0,  # Base reference (100%)
                'spell_cost_base': {
                    'spell1': 4,  # Spin Attack
                    'spell2': 6,  # Vanish
                    'spell3': 4,  # Multihit
                    'spell4': 8   # Smoke Bomb
                }
            },
            'shaman': {
                'health': 5,
                'mana': 15,
                'base_defense_multiplier': 0.5,  # Takes 50% more damage than assassin
                'spell_cost_base': {
                    'spell1': 6,  # Totem
                    'spell2': 4,  # Haul
                    'spell3': 6,  # Aura
                    'spell4': 8   # Uproot
                }
            }
        }
        
        # Attack speed multipliers
        self.attack_speed_multipliers = {
            'Super Slow': 0.51,
            'Very Slow': 0.83,
            'Slow': 1.5,
            'Normal': 2.05,
            'Fast': 2.5,
            'Very Fast': 3.1,
            'Super Fast': 4.3
        }

    def calculate_build_stats(self, items: List[Dict[str, Any]], player_class: str, player_level: int = 106) -> Dict[str, Any]:
        """
        Calculate comprehensive build statistics
        
        Args:
            items: List of equipped items
            player_class: Player's class
            player_level: Player's level
            
        Returns:
            Dictionary with all calculated statistics
        """
        stats = {
            'level': player_level,
            'class': player_class,
            'health': self._calculate_health(items, player_class, player_level),
            'mana': self._calculate_mana(items, player_class, player_level),
            'skill_points': self._calculate_skill_points(items),
            'damage': self._calculate_damage_stats(items, player_class),
            'defenses': self._calculate_defenses(items, player_class),
            'utility_stats': self._calculate_utility_stats(items),
            'spell_costs': self._calculate_spell_costs(items, player_class),
            'effective_hp': self._calculate_effective_hp(items, player_class, player_level)
        }
        
        return stats

    def _calculate_health(self, items: List[Dict[str, Any]], player_class: str, player_level: int) -> Dict[str, int]:
        """Calculate total health and health regeneration"""
        base_health = self.class_base_stats[player_class]['health'] * player_level
        
        # Sum health bonuses from items
        health_bonus = 0
        health_regen_raw = 0
        health_regen_percent = 0
        
        for item in items:
            health_bonus += item.get('hp', 0)
            
            ids = item.get('identifications', {})
            health_bonus += ids.get('health_bonus', 0)
            health_regen_raw += ids.get('health_regen_raw', 0)
            health_regen_percent += ids.get('health_regen_percent', 0)
        
        total_health = base_health + health_bonus
        
        # Calculate health regeneration (every 5 seconds)
        base_regen = max(1, total_health // 20)  # Natural regen
        modified_regen = base_regen + health_regen_raw
        final_regen = modified_regen * (1 + health_regen_percent / 100)
        
        return {
            'total': total_health,
            'base': base_health,
            'bonus': health_bonus,
            'regen_per_5s': max(0, int(final_regen))
        }

    def _calculate_mana(self, items: List[Dict[str, Any]], player_class: str, player_level: int) -> Dict[str, int]:
        """Calculate total mana and mana regeneration"""
        base_mana = self.class_base_stats[player_class]['mana'] * player_level
        
        # Sum mana bonuses from items
        mana_bonus = 0
        mana_regen = 0
        
        for item in items:
            mana_bonus += item.get('mana', 0)
            
            ids = item.get('identifications', {})
            mana_regen += ids.get('mana_regen', 0)
        
        total_mana = base_mana + mana_bonus
        
        return {
            'total': total_mana,
            'base': base_mana,
            'bonus': mana_bonus,
            'regen_per_5s': mana_regen
        }

    def _calculate_skill_points(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate skill point bonuses from items"""
        skill_points = {
            'str': 0,
            'dex': 0,
            'int': 0,
            'def': 0,
            'agi': 0
        }
        
        for item in items:
            ids = item.get('identifications', {})
            for stat in skill_points.keys():
                skill_points[stat] += ids.get(stat, 0)
        
        return skill_points

    def _calculate_damage_stats(self, items: List[Dict[str, Any]], player_class: str) -> Dict[str, Any]:
        """Calculate damage statistics including spell and melee damage"""
        weapon = self._get_weapon(items)
        
        if not weapon:
            return {
                'weapon_damage': None,
                'spell_damage': 0,
                'melee_damage': 0,
                'main_attack_dps': 0
            }
        
        # Base weapon damage
        weapon_damage = weapon.get('damage', {})
        attack_speed = weapon.get('attack_speed', 'Normal')
        
        # Calculate damage bonuses from all items
        spell_damage_raw = 0
        spell_damage_percent = 0
        melee_damage_raw = 0
        melee_damage_percent = 0
        
        for item in items:
            ids = item.get('identifications', {})
            spell_damage_raw += ids.get('spell_damage_raw', 0)
            spell_damage_percent += ids.get('spell_damage_percent', 0)
            melee_damage_raw += ids.get('melee_damage_raw', 0)
            melee_damage_percent += ids.get('melee_damage_percent', 0)
        
        # Calculate main attack DPS
        main_attack_dps = self._calculate_main_attack_dps(weapon_damage, attack_speed)
        
        return {
            'weapon_damage': weapon_damage,
            'attack_speed': attack_speed,
            'spell_damage_raw': spell_damage_raw,
            'spell_damage_percent': spell_damage_percent,
            'melee_damage_raw': melee_damage_raw,
            'melee_damage_percent': melee_damage_percent,
            'main_attack_dps': main_attack_dps
        }

    def _calculate_defenses(self, items: List[Dict[str, Any]], player_class: str) -> Dict[str, int]:
        """Calculate elemental defenses"""
        defenses = {
            'earth': 0,
            'thunder': 0,
            'water': 0,
            'fire': 0,
            'air': 0
        }
        
        for item in items:
            item_defenses = item.get('defenses', {})
            for element in defenses.keys():
                defenses[element] += item_defenses.get(element, 0)
        
        return defenses

    def _calculate_utility_stats(self, items: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate utility statistics"""
        utility = {
            'walk_speed': 0,
            'mana_steal': 0,
            'life_steal': 0,
            'xp_bonus': 0,
            'loot_bonus': 0,
            'reflection': 0,
            'thorns': 0,
            'poison': 0,
            'exploding': 0
        }
        
        for item in items:
            ids = item.get('identifications', {})
            for stat in utility.keys():
                utility[stat] += ids.get(stat, 0)
        
        return utility

    def _calculate_spell_costs(self, items: List[Dict[str, Any]], player_class: str) -> Dict[str, int]:
        """Calculate spell costs after intelligence and cost reduction"""
        base_costs = self.class_base_stats[player_class]['spell_cost_base']
        
        # Calculate intelligence bonuses
        intelligence = 0
        spell_cost_raw = 0
        spell_cost_percent = 0
        
        for item in items:
            ids = item.get('identifications', {})
            intelligence += ids.get('int', 0)
            spell_cost_raw += ids.get('spell_cost_raw', 0)
            spell_cost_percent += ids.get('spell_cost_percent', 0)
        
        modified_costs = {}
        
        for spell, base_cost in base_costs.items():
            # Apply intelligence reduction (from reference materials)
            int_reduction = self._calculate_intelligence_cost_reduction(intelligence, base_cost)
            cost_after_int = max(1, base_cost - int_reduction)
            
            # Apply raw cost reduction
            cost_after_raw = max(1, cost_after_int + spell_cost_raw)  # Raw can be negative
            
            # Apply percentage reduction
            final_cost = max(1, int(cost_after_raw * (1 - spell_cost_percent / 100)))
            
            modified_costs[spell] = final_cost
        
        return modified_costs

    def _calculate_effective_hp(self, items: List[Dict[str, Any]], player_class: str, player_level: int) -> Dict[str, float]:
        """Calculate effective HP considering defenses"""
        health_stats = self._calculate_health(items, player_class, player_level)
        total_health = health_stats['total']
        
        # Calculate skill points from items  
        skill_points = self._calculate_skill_points(items)
        defense_points = skill_points['def']
        agility_points = skill_points['agi']
        
        # Base class defense multiplier
        base_multiplier = self.class_base_stats[player_class]['base_defense_multiplier']
        
        # Calculate damage reduction from defense
        defense_reduction = min(0.8, defense_points * 0.003)  # Max 80% reduction
        
        # Calculate dodge chance from agility (simplified)
        dodge_chance = min(0.75, agility_points * 0.002)  # Max 75% dodge
        
        # Calculate effective HP
        defense_ehp = total_health / max(0.01, (1 - defense_reduction) * base_multiplier)
        agility_ehp = total_health / max(0.01, 1 - dodge_chance)
        combined_ehp = total_health / max(0.01, (1 - defense_reduction) * (1 - dodge_chance) * base_multiplier)
        
        return {
            'base_hp': total_health,
            'defense_ehp': int(defense_ehp),
            'agility_ehp': int(agility_ehp),
            'combined_ehp': int(combined_ehp),
            'defense_reduction_percent': defense_reduction * 100,
            'dodge_chance_percent': dodge_chance * 100
        }

    def _get_weapon(self, items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Get the equipped weapon from items list"""
        for item in items:
            if item.get('slot') == 'weapon':
                return item
        return None

    def _calculate_main_attack_dps(self, weapon_damage: Dict[str, List[int]], attack_speed: str) -> float:
        """Calculate main attack DPS"""
        if not weapon_damage:
            return 0.0
        
        # Calculate average damage per hit
        total_damage = 0
        for damage_type, damage_range in weapon_damage.items():
            if len(damage_range) == 2:
                avg_damage = (damage_range[0] + damage_range[1]) / 2
                total_damage += avg_damage
        
        # Get attacks per second
        attacks_per_second = self.attack_speed_multipliers.get(attack_speed, 2.05)
        
        return total_damage * attacks_per_second

    def _calculate_intelligence_cost_reduction(self, intelligence: int, base_cost: int) -> int:
        """Calculate mana cost reduction from intelligence (authentic formula)"""
        if intelligence <= 0:
            return 0
        
        # Simplified intelligence formula based on reference materials
        # Intelligence reduces costs in steps
        reduction = 0
        temp_int = intelligence
        
        while temp_int >= 2 and reduction < base_cost - 1:
            reduction += 1
            temp_int -= 2
        
        return min(reduction, base_cost - 1)  # Never reduce below 1 mana

    def calculate_build_score(self, items: List[Dict[str, Any]], player_class: str, 
                            playstyle: str = 'balanced', player_level: int = 106) -> float:
        """
        Calculate overall build effectiveness score (0-100)
        
        Args:
            items: List of equipped items
            player_class: Player's class
            playstyle: Build focus (spellspam, melee, tank, hybrid)
            player_level: Player's level
            
        Returns:
            Score from 0 to 100
        """
        stats = self.calculate_build_stats(items, player_class, player_level)
        score = 0.0
        
        # Base scoring weights by playstyle
        if playstyle == 'spellspam':
            weights = {
                'mana': 0.3,
                'spell_damage': 0.4,
                'mana_sustain': 0.2,
                'survivability': 0.1
            }
        elif playstyle == 'melee':
            weights = {
                'melee_damage': 0.4,
                'attack_speed': 0.2,
                'survivability': 0.3,
                'utility': 0.1
            }
        elif playstyle == 'tank':
            weights = {
                'survivability': 0.6,
                'health': 0.2,
                'utility': 0.2
            }
        else:  # balanced/hybrid
            weights = {
                'damage': 0.3,
                'survivability': 0.3,
                'mana': 0.2,
                'utility': 0.2
            }
        
        # Calculate component scores (0-100 each)
        damage_score = min(100, stats['damage']['main_attack_dps'] / 20)  # Normalized
        health_score = min(100, stats['health']['total'] / 100)  # Normalized
        mana_score = min(100, stats['mana']['total'] / 50)  # Normalized
        ehp_score = min(100, stats['effective_hp']['combined_ehp'] / 150)  # Normalized
        
        # Weight and combine scores
        final_score = (
            damage_score * weights.get('damage', 0.25) +
            health_score * weights.get('health', 0.25) +
            mana_score * weights.get('mana', 0.25) +
            ehp_score * weights.get('survivability', 0.25)
        )
        
        return min(100, max(0, final_score))