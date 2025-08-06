# WynnBuilder Enhanced CLI

An advanced command-line interface for generating optimized Wynncraft builds with comprehensive filtering, validation, and export capabilities.

## Features

### 🚀 Core Functionality
- **Complete Build Generation**: Creates full equipment sets (helmet, chestplate, leggings, boots, weapon, accessories)
- **Class-Specific Filtering**: Optimized for all 5 Wynncraft classes (Mage, Archer, Warrior, Assassin, Shaman)
- **Playstyle Optimization**: Specialized builds for spellspam, melee, hybrid, and tank playstyles
- **Skill Point Validation**: Ensures builds meet stat requirements with configurable SP limits (default: 200)
- **Intelligent Scoring**: Advanced scoring system using formula: `damage + mana_regen * 10 + ehp / 1000`

### 🎯 Advanced Filters
- **Level Filtering**: Filter items by maximum level requirement
- **Element Preference**: Optimize for specific elements (thunder, water, earth, fire, air)
- **Mythic Control**: Option to exclude mythic items from builds
- **Performance Thresholds**: Set minimum DPS and mana regeneration requirements
- **Build Limits**: Control number of results displayed (top N builds)

### 📊 Display & Export
- **Rich Terminal Output**: Beautiful tables and formatting using Rich library
- **Build Statistics**: Comprehensive stats including DPS, mana/s, EHP, and skill point breakdown
- **JSON Export**: Export builds to structured JSON files
- **Wynnbuilder Export**: Generate Wynnbuilder-compatible strings for easy sharing
- **Interactive Mode**: Step-by-step build configuration

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd wynnbuilder

# Install dependencies (already included)
pip install rich flask requests

# Ensure item data is available
python main.py  # Downloads latest item data automatically
```

## Usage

### Quick Start Examples

```bash
# Generate top 5 mage spellspam builds
python cli_enhanced.py --class mage --playstyle spellspam --top 5

# Create tank builds with level 105 cap
python cli_enhanced.py --class warrior --playstyle tank --max-level 105

# Thunder-focused archer builds without mythics
python cli_enhanced.py --class archer --element thunder --no-mythics

# Interactive mode for step-by-step configuration
python cli_enhanced.py --interactive

# Export builds to file
python cli_enhanced.py --class mage --export my_builds.json

# Generate Wynnbuilder export strings
python cli_enhanced.py --class shaman --export-wynnbuilder
```

### Command Line Options

```
Options:
  --class {mage,archer,warrior,assassin,shaman}
                        Filter builds by class
  --max-level MAX_LEVEL
                        Maximum item level (default: 106)
  --playstyle {spellspam,melee,hybrid,tank}
                        Filter by playstyle
  --element {thunder,water,earth,fire,air}
                        Preferred element for builds
  --top TOP             Number of top builds to display (default: 10)
  --max-sp MAX_SP       Maximum skill points (default: 200)
  --no-mythics          Exclude mythic items from builds
  --min-dps MIN_DPS     Minimum DPS requirement
  --min-mana MIN_MANA   Minimum mana regeneration requirement
  --export EXPORT       Export builds to JSON file
  --export-wynnbuilder  Export builds as Wynnbuilder-compatible strings
  --interactive         Run in interactive mode
  --scoring-formula SCORING_FORMULA
                        Custom scoring formula (advanced users)
```

### Interactive Mode

For users who prefer guided configuration:

```bash
python cli_enhanced.py --interactive
```

This mode will prompt you through:
1. Class selection
2. Playstyle preference
3. Level and skill point limits
4. Element preferences
5. Mythic item inclusion
6. Number of results

## Technical Implementation

### Architecture
```
/core
├── builder.py      # Build generation and validation logic
├── filters.py      # Item filtering and optimization
├── stats.py        # Damage and stat calculations
└── loader.py       # Item data loading and management

/data
└── items.json      # 4,186+ current Wynncraft items

cli_enhanced.py     # Enhanced CLI interface
web_interface.py    # Web application (runs simultaneously)
```

### Key Algorithms

**Build Generation**: Uses itertools.product for comprehensive equipment combinations with intelligent pre-filtering to manage computational complexity.

**Validation System**: 
- Skill point requirement validation (configurable 200 SP limit)
- Stat threshold checking (DPS, mana, EHP)
- Equipment compatibility verification

**Scoring System**:
```python
score = damage + (mana_regen * 10) + (ehp / 1000)
```

**Data Source**: Live data from WynnBuilder GitHub repository (4,186 items)

### Performance Optimizations
- **Pre-filtering**: Reduces item pool before combination generation
- **Batch Validation**: Efficient build validation pipeline
- **Smart Limits**: Prevents combinatorial explosion with reasonable constraints
- **Caching**: Item data cached for improved performance

## Web Interface Integration

The CLI runs alongside a full web interface accessible at `http://localhost:5000`:

- **Build Generator**: Interactive web form for build generation
- **AI Assistant**: Natural language queries about builds and game mechanics
- **Real-time Results**: Live build generation with visual statistics
- **Export Tools**: Web-based export to multiple formats

## Export Formats

### JSON Export
```json
{
  "id": 1,
  "class": "mage",
  "score": 1250.5,
  "items": {
    "weapon": {"name": "Weathered", "level": 105, "tier": "Legendary"},
    "helmet": {"name": "Morph-Iron", "level": 105, "tier": "Unique"}
  },
  "stats": {
    "dps": 850.2,
    "mana": 4.5,
    "ehp": 12000,
    "skill_points": {"str": 0, "dex": 15, "int": 85, "def": 25, "agi": 0}
  }
}
```

### Wynnbuilder Export
```
CR_05+06_003000_015010_000X00_00U00_002005
```
Direct import into Wynnbuilder website for further customization.

## Advanced Features

### Custom Scoring (Advanced)
```bash
python cli_enhanced.py --scoring-formula "custom_function"
```

### Batch Processing
```bash
# Generate builds for all classes
for class in mage archer warrior assassin shaman; do
    python cli_enhanced.py --class $class --top 3 --export ${class}_builds.json
done
```

### Performance Monitoring
The system automatically limits build generation to prevent excessive computation while maintaining comprehensive coverage of viable builds.

## Data Integrity

- **Authentic Data**: Uses real Wynncraft item data from official WynnBuilder repository
- **Live Updates**: Item data refreshed automatically from GitHub
- **Validation**: All builds validated against actual game mechanics
- **Accuracy**: Implements authentic Wynncraft damage formulas and stat calculations

## Troubleshooting

### Common Issues

**"No valid builds found"**: 
- Reduce filter constraints (lower min-dps, increase max-sp)
- Try different playstyle or class combinations
- Check if mythic items are needed for viable builds

**Slow Performance**:
- Reduce --top value for fewer results
- Use more specific filters to reduce item pool
- Consider excluding mythics with --no-mythics

**Missing Items**:
- Restart application to refresh item data
- Check internet connection for data download

### Support

For technical issues or feature requests, the application includes comprehensive error handling and helpful error messages.

## Integration with Main Application

This CLI tool is fully integrated with the main WynnBuilder application:

- **Shared Core**: Uses same build generation and validation logic as web interface
- **Data Consistency**: Identical item database and calculations
- **Export Compatibility**: Full compatibility with web interface exports
- **Parallel Operation**: Can run simultaneously with web server

Start the complete application with:
```bash
python main.py  # Starts web server on port 5000
python cli_enhanced.py --interactive  # Run CLI in separate terminal
```