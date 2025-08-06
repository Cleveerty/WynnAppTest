"""
Build validation system for Wynncraft builds
Validates class requirements, level requirements, skill point constraints, and item compatibility
"""

from typing import Dict, List, Any, Tuple, Optional

class BuildValidator:
    """Validates Wynncraft builds for compliance with game rules"""
    
    def __init__(self):
        # Maximum skill points at level 106 (2 per level + 10 base)
        self.max_skill_points = 200
        
        # Class-weapon compatibility 
        self.class_weapons = {
            'mage': ['wand'],
            'archer': ['bow'], 
            'warrior': ['spear'],
            'assassin': ['dagger'],
            'shaman': ['relik']
        }
        
        # Equipment slots that can only have one item
        self.unique_slots = ['helmet', 'chestplate', 'leggings', 'boots', 'weapon', 'bracelet', 'necklace']
        
        # Slots that can have multiple items
        self.multi_slots = ['ring']  # Can have 2 rings

    def validate_build(self, items: List[Dict[str, Any]], player_class: str, player_level: int = 106) -> Dict[str, Any]:
        """
        Comprehensive build validation
        
        Args:
            items: List of equipped items
            player_class: Player's class (mage, archer, etc.)
            player_level: Player's level (default 106)
            
        Returns:
            Dictionary with validation results and details
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        # Basic validation checks
        self._validate_item_slots(items, validation_result)
        self._validate_class_requirements(items, player_class, validation_result)
        self._validate_level_requirements(items, player_level, validation_result)
        
        # Calculate and validate skill points
        skill_points = self._calculate_skill_point_requirements(items)
        validation_result['stats']['skill_points_required'] = skill_points
        validation_result['stats']['skill_points_available'] = self._calculate_available_skill_points(player_level)
        
        self._validate_skill_points(skill_points, player_level, validation_result)
        
        # Validate item compatibility
        self._validate_item_compatibility(items, validation_result)
        
        # Set overall validity
        validation_result['valid'] = len(validation_result['errors']) == 0
        
        return validation_result

    def _validate_item_slots(self, items: List[Dict[str, Any]], result: Dict[str, Any]):
        """Validate equipment slot constraints"""
        slot_counts = {}
        
        for item in items:
            slot = item.get('slot', 'unknown')
            slot_counts[slot] = slot_counts.get(slot, 0) + 1
        
        # Check unique slot constraints
        for slot in self.unique_slots:
            if slot_counts.get(slot, 0) > 1:
                result['errors'].append(f"Cannot equip more than 1 {slot}")
        
        # Check multi-slot constraints
        if slot_counts.get('ring', 0) > 2:
            result['errors'].append("Cannot equip more than 2 rings")

    def _validate_class_requirements(self, items: List[Dict[str, Any]], player_class: str, result: Dict[str, Any]):
        """Validate class requirements for items"""
        player_class = player_class.lower()
        allowed_weapons = self.class_weapons.get(player_class, [])
        
        for item in items:
            # Check weapon type restrictions
            if item.get('slot') == 'weapon':
                weapon_type = item.get('type', '').lower()
                if weapon_type not in allowed_weapons:
                    result['errors'].append(
                        f"{item.get('name', 'Unknown')} is a {weapon_type}, but {player_class} can only use {', '.join(allowed_weapons)}"
                    )
            
            # Check explicit class requirements
            item_class_req = item.get('classReq', '').lower()
            if item_class_req and item_class_req != player_class:
                result['errors'].append(
                    f"{item.get('name', 'Unknown')} requires {item_class_req.title()} class"
                )

    def _validate_level_requirements(self, items: List[Dict[str, Any]], player_level: int, result: Dict[str, Any]):
        """Validate level requirements for items"""
        for item in items:
            item_level = item.get('lvl', 0)
            if item_level > player_level:
                result['errors'].append(
                    f"{item.get('name', 'Unknown')} requires level {item_level} (you are level {player_level})"
                )

    def _calculate_skill_point_requirements(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate total skill point requirements for build"""
        total_requirements = {
            'str': 0,
            'dex': 0,
            'int': 0,
            'def': 0,
            'agi': 0
        }
        
        for item in items:
            for stat in total_requirements.keys():
                req_key = f'{stat}Req'
                requirement = item.get(req_key, 0)
                total_requirements[stat] = max(total_requirements[stat], requirement)
        
        return total_requirements

    def _calculate_available_skill_points(self, player_level: int) -> int:
        """Calculate available skill points at given level"""
        # Base: 10 skill points + 2 per level
        return min(10 + (player_level * 2), self.max_skill_points)

    def _validate_skill_points(self, requirements: Dict[str, int], player_level: int, result: Dict[str, Any]):
        """Validate skill point allocation"""
        available_points = self._calculate_available_skill_points(player_level)
        required_points = sum(requirements.values())
        
        result['stats']['skill_points_used'] = required_points
        
        if required_points > available_points:
            result['errors'].append(
                f"Build requires {required_points} skill points, but only {available_points} are available at level {player_level}"
            )
        
        # Check individual requirements
        for stat, requirement in requirements.items():
            if requirement > 0:
                max_stat_points = available_points  # Could invest all points in one stat
                if requirement > max_stat_points:
                    result['errors'].append(
                        f"Impossible {stat.upper()} requirement: {requirement} (max possible: {max_stat_points})"
                    )

    def _validate_item_compatibility(self, items: List[Dict[str, Any]], result: Dict[str, Any]):
        """Validate item compatibility and conflicts"""
        # Check for quest-required items
        quest_items = [item for item in items if item.get('quest_req')]
        if quest_items:
            quest_names = [item.get('quest_req') for item in quest_items]
            result['warnings'].append(f"Build includes quest-required items: {', '.join(quest_names)}")
        
        # Check for untradeable items
        untradeable_items = [item for item in items if item.get('untradeable')]
        if untradeable_items:
            item_names = [item.get('name', 'Unknown') for item in untradeable_items]
            result['warnings'].append(f"Build includes untradeable items: {', '.join(item_names)}")
        
        # Check for extremely high-level items
        mythic_items = [item for item in items if item.get('tier') == 'Mythic']
        if mythic_items:
            item_names = [item.get('name', 'Unknown') for item in mythic_items]
            result['warnings'].append(f"Build includes Mythic items (extremely rare): {', '.join(item_names)}")

    def validate_item_for_class(self, item: Dict[str, Any], player_class: str) -> bool:
        """Check if a single item can be used by the given class"""
        player_class = player_class.lower()
        
        # Check weapon type
        if item.get('slot') == 'weapon':
            weapon_type = item.get('type', '').lower()
            allowed_weapons = self.class_weapons.get(player_class, [])
            if weapon_type not in allowed_weapons:
                return False
        
        # Check explicit class requirement
        item_class_req = item.get('classReq', '').lower()
        if item_class_req and item_class_req != player_class:
            return False
        
        return True

    def check_skill_point_feasibility(self, items: List[Dict[str, Any]], player_level: int = 106) -> Tuple[bool, Dict[str, int]]:
        """
        Check if skill point requirements are feasible
        
        Returns:
            (feasible, requirements_dict)
        """
        requirements = self._calculate_skill_point_requirements(items)
        available = self._calculate_available_skill_points(player_level)
        total_required = sum(requirements.values())
        
        return total_required <= available, requirements

    def get_build_efficiency_score(self, items: List[Dict[str, Any]], player_class: str, player_level: int = 106) -> float:
        """
        Calculate build efficiency score (0.0 to 1.0)
        
        Factors:
        - Skill point efficiency (not wasting points)
        - Level appropriateness
        - Class synergy
        """
        validation = self.validate_build(items, player_class, player_level)
        
        if not validation['valid']:
            return 0.0
        
        score = 1.0
        
        # Penalty for warnings
        warning_penalty = len(validation['warnings']) * 0.1
        score -= min(warning_penalty, 0.5)  # Max 50% penalty for warnings
        
        # Skill point efficiency
        available_sp = validation['stats']['skill_points_available']
        used_sp = validation['stats']['skill_points_used']
        
        if available_sp > 0:
            sp_efficiency = used_sp / available_sp
            # Penalty for very low or very high usage
            if sp_efficiency < 0.3:  # Using too few points
                score -= 0.2
            elif sp_efficiency > 0.95:  # Using almost all points (risky)
                score -= 0.1
        
        # Level appropriateness
        item_levels = [item.get('lvl', 0) for item in items if item.get('lvl', 0) > 0]
        if item_levels:
            avg_item_level = sum(item_levels) / len(item_levels)
            level_diff = abs(avg_item_level - player_level)
            
            if level_diff > 20:  # Items very different from player level
                score -= 0.15
        
        return max(0.0, min(1.0, score))

    def suggest_improvements(self, items: List[Dict[str, Any]], player_class: str, player_level: int = 106) -> List[str]:
        """Suggest improvements for the build"""
        suggestions = []
        validation = self.validate_build(items, player_class, player_level)
        
        if validation['errors']:
            suggestions.append("Fix validation errors before using this build")
        
        # Skill point suggestions
        requirements = validation['stats'].get('skill_points_required', {})
        used_sp = sum(requirements.values())
        available_sp = validation['stats'].get('skill_points_available', 0)
        
        if used_sp < available_sp * 0.5:
            suggestions.append("Consider using higher-level items to make better use of skill points")
        
        if used_sp > available_sp * 0.9:
            suggestions.append("Build uses almost all skill points - consider more flexible alternatives")
        
        # Tier distribution suggestions
        tiers = [item.get('tier', 'Normal') for item in items]
        mythic_count = tiers.count('Mythic')
        legendary_count = tiers.count('Legendary')
        
        if mythic_count > 2:
            suggestions.append("Multiple Mythic items may be difficult to obtain")
        
        if mythic_count + legendary_count == 0 and player_level > 80:
            suggestions.append("Consider including some Legendary items for better stats at your level")
        
        return suggestions