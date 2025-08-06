"""
HTML Ability Extractor for Wynncraft
Extracts ability names and descriptions from HTML files containing ability data
"""

import re
import json
from typing import List, Dict, Any
from pathlib import Path
from bs4 import BeautifulSoup


class AbilityExtractor:
    """Extracts ability information from HTML files"""
    
    def __init__(self):
        self.abilities = []
    
    def extract_from_html(self, html_content: str) -> List[Dict[str, str]]:
        """
        Extract abilities from HTML content containing <td class="ability-info-row"> blocks
        
        Args:
            html_content: Raw HTML content as string
            
        Returns:
            List of dictionaries with 'name' and 'description' keys
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        abilities = []
        
        # Find all ability info rows
        ability_rows = soup.find_all('td', class_='ability-info-row')
        
        for row in ability_rows:
            try:
                # Find the ability name in <u> tags
                u_tag = row.find('u')
                if not u_tag:
                    continue
                
                ability_name = u_tag.get_text().strip()
                if not ability_name:
                    continue
                
                # Remove the <u> tag to get clean description
                u_tag.extract()
                
                # Get the remaining text as description
                description = row.get_text().strip()
                
                # Clean up whitespace and normalize
                description = re.sub(r'\s+', ' ', description).strip()
                
                if description:
                    abilities.append({
                        'name': ability_name,
                        'description': description
                    })
                    
            except Exception as e:
                print(f"Error processing ability row: {e}")
                continue
        
        return abilities
    
    def extract_from_file(self, file_path: str) -> List[Dict[str, str]]:
        """
        Extract abilities from HTML file
        
        Args:
            file_path: Path to HTML file
            
        Returns:
            List of dictionaries with ability data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return self.extract_from_html(html_content)
        except FileNotFoundError:
            print(f"HTML file not found: {file_path}")
            return []
        except Exception as e:
            print(f"Error reading HTML file: {e}")
            return []
    
    def save_abilities_json(self, abilities: List[Dict[str, str]], output_path: str):
        """Save extracted abilities to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(abilities, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(abilities)} abilities to {output_path}")
        except Exception as e:
            print(f"Error saving abilities: {e}")
    
    def create_sample_abilities(self) -> List[Dict[str, str]]:
        """Create sample Wynncraft Mage abilities for testing"""
        return [
            {
                "name": "Meteor",
                "description": "Has an auto-aim radius of 2 blocks where the meteor lands. Deals massive fire damage in a large area."
            },
            {
                "name": "Shooting Star",
                "description": "Doubles the speed of Meteor, making it only take 1s to cast instead of 2s."
            },
            {
                "name": "Wand Proficiency I",
                "description": "Improves your Main Attack's damage and range when using a wand by 5%."
            },
            {
                "name": "Cheaper Heal",
                "description": "Reduces the mana cost of Heal by 2 points."
            },
            {
                "name": "Heal",
                "description": "Heals you and nearby players. Base healing scales with your level."
            },
            {
                "name": "Teleport",
                "description": "Instantly teleport forward 8 blocks. Can pass through walls."
            },
            {
                "name": "Ice Snake",
                "description": "Summons a snake of ice that travels forward, dealing water damage and slowing enemies."
            },
            {
                "name": "Cheaper Teleport",
                "description": "Reduces the mana cost of Teleport by 2 points."
            },
            {
                "name": "Cheaper Meteor",
                "description": "Reduces the mana cost of Meteor by 2 points."
            },
            {
                "name": "Earth Mastery",
                "description": "Increases your earth damage by 15% and gives +2 to earth defense."
            },
            {
                "name": "Thunder Mastery",
                "description": "Increases your thunder damage by 15% and gives +2 to thunder defense."
            },
            {
                "name": "Water Mastery",
                "description": "Increases your water damage by 15% and gives +2 to water defense."
            },
            {
                "name": "Fire Mastery",
                "description": "Increases your fire damage by 15% and gives +2 to fire defense."
            },
            {
                "name": "Air Mastery",
                "description": "Increases your air damage by 15% and gives +2 to air defense."
            }
        ]


def main():
    """Main function for testing ability extraction"""
    extractor = AbilityExtractor()
    
    # Check if HTML file exists, otherwise create sample data
    html_file = "abilities.html"
    
    if Path(html_file).exists():
        print(f"Extracting abilities from {html_file}...")
        abilities = extractor.extract_from_file(html_file)
    else:
        print("No HTML file found, creating sample Mage abilities...")
        abilities = extractor.create_sample_abilities()
    
    if abilities:
        print(f"\nExtracted {len(abilities)} abilities:")
        for i, ability in enumerate(abilities, 1):
            print(f"{i}. {ability['name']}: {ability['description']}")
        
        # Save to JSON
        output_file = "data/mage_abilities.json"
        Path("data").mkdir(exist_ok=True)
        extractor.save_abilities_json(abilities, output_file)
    else:
        print("No abilities extracted")


if __name__ == "__main__":
    main()