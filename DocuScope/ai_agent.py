"""
AI Assistant module for intelligent build suggestions and query processing
"""

import os
import json
import re
from typing import List, Dict, Any, Optional

class WynnAI:
    """AI assistant for Wynncraft build generation and advice."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "demo_key")
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load game knowledge base for AI responses."""
        return {
            'classes': {
                'mage': {
                    'strengths': ['High spell damage', 'Area damage', 'Elemental focus'],
                    'weaknesses': ['Low defense', 'Mana dependent'],
                    'recommended_stats': ['Intelligence', 'Spell Damage', 'Mana Regen'],
                    'spells': ['Meteor', 'Ice Snake', 'Teleport', 'Heal']
                },
                'archer': {
                    'strengths': ['Ranged damage', 'High DPS', 'Mobility'],
                    'weaknesses': ['Lower defense', 'Position dependent'],
                    'recommended_stats': ['Dexterity', 'Attack Speed', 'Critical Hit'],
                    'spells': ['Arrow Storm', 'Escape', 'Bomb', 'Arrow Shield']
                },
                'warrior': {
                    'strengths': ['High defense', 'Melee damage', 'Tanky'],
                    'weaknesses': ['Lower mobility', 'Mana issues'],
                    'recommended_stats': ['Strength', 'Defense', 'Health'],
                    'spells': ['Bash', 'Charge', 'Uppercut', 'War Scream']
                },
                'assassin': {
                    'strengths': ['Very high DPS', 'Critical hits', 'Mobility'],
                    'weaknesses': ['Very low defense', 'Glass cannon'],
                    'recommended_stats': ['Dexterity', 'Agility', 'Critical Hit'],
                    'spells': ['Spin Attack', 'Vanish', 'Multihit', 'Smoke Bomb']
                },
                'shaman': {
                    'strengths': ['Support abilities', 'Healing', 'Balanced'],
                    'weaknesses': ['Complex mechanics', 'Team dependent'],
                    'recommended_stats': ['Intelligence', 'Agility', 'Mana Regen'],
                    'spells': ['Totem', 'Haul', 'Aura', 'Uproot']
                }
            },
            'elements': {
                'earth': {'damage_type': 'consistent', 'special': 'high_damage'},
                'thunder': {'damage_type': 'variable', 'special': 'chain_damage'},
                'water': {'damage_type': 'healing', 'special': 'mana_steal'},
                'fire': {'damage_type': 'burn', 'special': 'damage_over_time'},
                'air': {'damage_type': 'knockback', 'special': 'mobility'}
            },
            'playstyles': {
                'spellspam': {
                    'focus': 'spell_damage',
                    'priority_stats': ['Intelligence', 'Mana Regen', 'Spell Damage'],
                    'avoid_stats': ['Attack Speed', 'Melee Damage']
                },
                'melee': {
                    'focus': 'melee_damage',
                    'priority_stats': ['Strength/Dexterity', 'Attack Speed', 'Critical Hit'],
                    'avoid_stats': ['Spell Damage', 'Mana Regen']
                },
                'hybrid': {
                    'focus': 'balanced',
                    'priority_stats': ['Mixed stats', 'Health', 'Mana'],
                    'avoid_stats': ['Extreme specialization']
                },
                'tank': {
                    'focus': 'survivability',
                    'priority_stats': ['Health', 'Defense', 'Health Regen'],
                    'avoid_stats': ['Glass cannon stats']
                }
            }
        }
    
    def process_query(self, query: str, items: List[Dict]) -> str:
        """Process natural language queries about builds."""
        query_lower = query.lower()
        
        # Pattern matching for common queries
        if any(word in query_lower for word in ['best', 'top', 'optimal']):
            return self._handle_best_build_query(query_lower, items)
        
        elif any(word in query_lower for word in ['compare', 'versus', 'vs', 'difference']):
            return self._handle_comparison_query(query_lower, items)
        
        elif any(word in query_lower for word in ['explain', 'how', 'why', 'what']):
            return self._handle_explanation_query(query_lower)
        
        elif any(word in query_lower for word in ['recommend', 'suggest', 'advice']):
            return self._handle_recommendation_query(query_lower, items)
        
        elif any(word in query_lower for word in ['fix', 'improve', 'optimize']):
            return self._handle_optimization_query(query_lower)
        
        else:
            return self._handle_general_query(query_lower)
    
    def _handle_best_build_query(self, query: str, items: List[Dict]) -> str:
        """Handle queries about best builds."""
        class_mentioned = None
        playstyle_mentioned = None
        
        # Extract class
        for class_name in self.knowledge_base['classes'].keys():
            if class_name in query:
                class_mentioned = class_name
                break
        
        # Extract playstyle
        for playstyle in self.knowledge_base['playstyles'].keys():
            if playstyle in query:
                playstyle_mentioned = playstyle
                break
        
        response = "For the best build, I'd recommend:\n\n"
        
        if class_mentioned:
            class_info = self.knowledge_base['classes'][class_mentioned]
            response += f"🏆 **{class_mentioned.title()} Build Focus:**\n"
            response += f"• Strengths: {', '.join(class_info['strengths'])}\n"
            response += f"• Key Stats: {', '.join(class_info['recommended_stats'])}\n"
            
            if playstyle_mentioned:
                playstyle_info = self.knowledge_base['playstyles'][playstyle_mentioned]
                response += f"\n🎯 **{playstyle_mentioned.title()} Strategy:**\n"
                response += f"• Priority: {', '.join(playstyle_info['priority_stats'])}\n"
                response += f"• Avoid: {', '.join(playstyle_info['avoid_stats'])}\n"
        
        response += "\n💡 **General Tips:**\n"
        response += "• Use the build generator with specific filters\n"
        response += "• Consider your preferred elements\n"
        response += "• Balance damage with survivability\n"
        response += "• Check mana sustain for spell builds"
        
        return response
    
    def _handle_comparison_query(self, query: str, items: List[Dict]) -> str:
        """Handle comparison queries."""
        return ("🔍 **Build Comparison Guide:**\n\n"
                "• **DPS vs Tank:** High damage but low survivability vs high defense but lower damage\n"
                "• **Spellspam vs Melee:** Mana-dependent ranged vs consistent close combat\n"
                "• **Mythic vs Legendary:** Unique effects vs reliable stats\n"
                "• **Mono-element vs Mixed:** Specialized damage vs balanced coverage\n\n"
                "💡 Use the build generator to create both builds and compare their stats!")
    
    def _handle_explanation_query(self, query: str) -> str:
        """Handle explanation queries."""
        if 'damage' in query:
            return ("📊 **Damage Calculation Explained:**\n\n"
                    "• **Spell Damage:** Base weapon damage × spell conversions × elemental bonuses\n"
                    "• **Powder Effects:** Convert neutral damage to elemental\n"
                    "• **Critical Hits:** Increase damage by critical multiplier\n"
                    "• **Weaknesses:** Extra damage against vulnerable enemies\n\n"
                    "🔧 The tool uses authentic Wynncraft formulas for accurate calculations!")
        
        elif 'mana' in query:
            return ("🔵 **Mana System Explained:**\n\n"
                    "• **Mana Regen:** Passive mana restoration per second\n"
                    "• **Mana Steal:** Gain mana on enemy hits\n"
                    "• **Intelligence:** Reduces spell costs\n"
                    "• **Spell Costs:** Base cost × (1 - INT%) + raw modifiers\n\n"
                    "⚡ Higher tier spells cost more but deal more damage!")
        
        elif 'ehp' in query or 'effective hp' in query:
            return ("❤️ **Effective HP (EHP) Explained:**\n\n"
                    "• **Formula:** HP × defense multipliers\n"
                    "• **Defense:** Reduces incoming damage\n"
                    "• **Agility:** Provides dodge chance\n"
                    "• **Resistances:** Reduce elemental damage\n\n"
                    "🛡️ EHP shows your true survivability accounting for all defensive stats!")
        
        else:
            return ("❓ **General Game Mechanics:**\n\n"
                    "• **Skill Points:** Maximum 120 points across all stats\n"
                    "• **Attack Speed:** Affects spell damage multipliers\n"
                    "• **Powder Slots:** Add elemental damage and conversions\n"
                    "• **Item Tiers:** Normal < Unique < Rare < Legendary < Mythic\n\n"
                    "📚 Ask about specific mechanics for detailed explanations!")
    
    def _handle_recommendation_query(self, query: str, items: List[Dict]) -> str:
        """Handle recommendation queries."""
        return ("🎯 **Build Recommendations:**\n\n"
                "**For New Players:**\n"
                "• Start with Warrior or Archer for easier gameplay\n"
                "• Focus on Unique/Rare items before Legendaries\n"
                "• Prioritize survivability over pure damage\n\n"
                "**For Advanced Players:**\n"
                "• Experiment with Mythic item combinations\n"
                "• Try mono-element builds for maximum damage\n"
                "• Consider hybrid builds for versatility\n\n"
                "**Current Meta:**\n"
                "• Thunder builds for high DPS\n"
                "• Water builds for sustain\n"
                "• Earth builds for consistent damage\n\n"
                "🔨 Use the build generator with your preferences for personalized recommendations!")
    
    def _handle_optimization_query(self, query: str) -> str:
        """Handle optimization queries."""
        return ("⚡ **Build Optimization Tips:**\n\n"
                "**Damage Optimization:**\n"
                "• Focus on one element for maximum conversion\n"
                "• Use powders that match your element\n"
                "• Stack spell damage % and raw spell damage\n"
                "• Consider attack speed for spell damage multipliers\n\n"
                "**Survivability Optimization:**\n"
                "• Balance HP with defense for maximum EHP\n"
                "• Add health regen for sustained combat\n"
                "• Use resistances against common damage types\n\n"
                "**Mana Optimization:**\n"
                "• Combine mana regen with mana steal\n"
                "• Invest in Intelligence for cost reduction\n"
                "• Consider lower tier spells for efficiency\n\n"
                "🎛️ Use the build generator's filters to optimize for specific goals!")
    
    def _handle_general_query(self, query: str) -> str:
        """Handle general queries."""
        return ("🤖 **AI Assistant Help:**\n\n"
                "I can help you with:\n"
                "• **Build recommendations** - Ask about the best builds for your class/playstyle\n"
                "• **Comparisons** - Compare different builds, items, or strategies\n"
                "• **Explanations** - Learn how damage, mana, or other mechanics work\n"
                "• **Optimization** - Get tips to improve your builds\n\n"
                "**Example questions:**\n"
                "• \"What's the best mage spellspam build?\"\n"
                "• \"How does spell damage calculation work?\"\n"
                "• \"Compare thunder vs fire builds\"\n"
                "• \"How can I optimize my mana sustain?\"\n\n"
                "💡 Try asking more specific questions for better help!")
    
    def suggest_build_alternatives(self, config: Dict[str, Any]) -> Optional[str]:
        """Suggest alternatives when no builds are found."""
        suggestions = []
        
        filters = config.get('filters', {})
        
        if filters.get('min_dps', 0) > 15000:
            suggestions.append("• Try lowering the minimum DPS requirement")
        
        if filters.get('min_mana_regen', 0) > 8:
            suggestions.append("• Consider reducing minimum mana regen")
        
        if config.get('no_mythics', False):
            suggestions.append("• Allow mythic items for more build options")
        
        if len(config.get('elements', [])) > 2:
            suggestions.append("• Focus on fewer elements for better synergy")
        
        if not suggestions:
            suggestions.append("• Try a different class or playstyle combination")
            suggestions.append("• Reduce filter requirements")
            suggestions.append("• Consider hybrid builds for more flexibility")
        
        return "Try these alternatives:\n" + "\n".join(suggestions) if suggestions else None
    
    def explain_build_stats(self, build_stats: Dict[str, float]) -> str:
        """Explain what build stats mean."""
        explanation = "📊 **Your Build Stats:**\n\n"
        
        dps = build_stats.get('dps', 0)
        if dps > 20000:
            explanation += f"💀 DPS: {dps:.0f} - Excellent damage output!\n"
        elif dps > 15000:
            explanation += f"💀 DPS: {dps:.0f} - Good damage for most content\n"
        elif dps > 10000:
            explanation += f"💀 DPS: {dps:.0f} - Decent damage, consider improvements\n"
        else:
            explanation += f"💀 DPS: {dps:.0f} - Low damage, focus on damage stats\n"
        
        mana = build_stats.get('mana', 0)
        if mana > 8:
            explanation += f"🔵 Mana: {mana:.1f}/s - Excellent sustain for spellspam\n"
        elif mana > 5:
            explanation += f"🔵 Mana: {mana:.1f}/s - Good sustain for regular casting\n"
        elif mana > 2:
            explanation += f"🔵 Mana: {mana:.1f}/s - Basic sustain, manage carefully\n"
        else:
            explanation += f"🔵 Mana: {mana:.1f}/s - Low sustain, avoid heavy spell usage\n"
        
        ehp = build_stats.get('ehp', 0)
        if ehp > 25000:
            explanation += f"❤️ EHP: {ehp:.0f} - Excellent survivability\n"
        elif ehp > 18000:
            explanation += f"❤️ EHP: {ehp:.0f} - Good survivability for most content\n"
        elif ehp > 12000:
            explanation += f"❤️ EHP: {ehp:.0f} - Decent survivability, be careful\n"
        else:
            explanation += f"❤️ EHP: {ehp:.0f} - Low survivability, very risky\n"
        
        return explanation
