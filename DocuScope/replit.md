# Overview

WynnBuilder is an advanced command-line and web-based build generator tool for Wynncraft MMORPG. It helps players create optimal character builds by analyzing item combinations, calculating spell damage, effective HP, mana sustain, and other combat statistics. The application features both CLI and web interfaces, integrates AI assistance for intelligent build suggestions, and provides compatibility with the popular Wynnbuilder website through export functionality.

## Recent Updates (August 2025)

**✓ Successfully Deployed Web Application**: Running Flask server on port 5000 with full functionality
**✓ Enhanced Interactive CLI**: Implemented modern terminal interface with fuzzy search and live autocompletion using prompt_toolkit and rapidfuzz
**✓ Authentic Item Database**: Successfully loaded 4,186 current Wynncraft items from existing data/items.json (1813 weapons, 726 accessories, 1647 armor pieces)
**✓ Advanced Autocomplete System**: Live item search with fuzzy matching, tier-based color coding, and smart filtering by class/level requirements
**✓ HTML Ability Extraction**: BeautifulSoup4-powered system extracts ability names and descriptions from HTML files with <td class="ability-info-row"> structure
**✓ Interactive Ability Selection**: Seamless ability selection workflow integrated into CLI with add/remove functionality and build summary display
**✓ Dropdown-Based Interface**: Modern dropdown CLI with radio buttons, checkboxes, and search dialogs - no typing required for selections
**✓ Comprehensive Build Tools**: Build validation with 200 SP limit, authentic damage calculations, and Wynnbuilder export compatibility
**✓ Modular Architecture**: Separate modules for autocomplete, build validation, stat calculation, ability extraction, and export functionality

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Application Structure
The project follows a modular architecture with clear separation of concerns:

- **Multi-Interface Design**: Supports both CLI (using Rich library for modern terminal UI) and web interfaces (Flask-based) for different user preferences
- **Core Processing Engine**: Centralized business logic in the `core/` package handling item loading, build generation, filtering, and statistics calculation
- **AI Integration**: OpenAI API integration for intelligent build recommendations and natural language query processing
- **Export System**: Wynnbuilder-compatible build export functionality for seamless integration with the wider Wynncraft community

## Data Management
- **JSON-based Item Database**: Loads item data from Wynnbuilder's GitHub repository, maintaining compatibility with the established ecosystem
- **In-memory Processing**: Items are cached in memory for fast build generation and filtering operations
- **Class-based Configuration**: Separate JSON configuration for class-specific mechanics, spells, and damage calculations

## Build Generation Algorithm
- **Combinatorial Generation**: Generates all viable equipment combinations using itertools for comprehensive build exploration
- **Multi-stage Filtering**: Pre-filters items by class, playstyle, and user constraints before combination generation to manage computational complexity
- **Validation System**: Validates builds against skill point requirements, stat thresholds, and equipment compatibility
- **Statistical Analysis**: Implements authentic Wynncraft damage formulas for spell damage, effective HP, and mana sustain calculations

## User Interface Design
- **Dropdown-Based CLI**: Modern dropdown interface using prompt_toolkit with radio buttons, checkboxes, and search dialogs
- **Interactive CLI with Autocomplete**: Advanced terminal interface with live fuzzy search, arrow key navigation, and tier-based color coding
- **Rich Formatting**: Comprehensive visual feedback with Rich library for progress bars, tables, panels, and colored output
- **Web Dashboard**: Bootstrap-based responsive web interface with real-time build generation and AI chat functionality
- **Multiple Interface Options**: Web, dropdown CLI, and advanced CLI interfaces all share authentic data sources

## AI Assistant Architecture
- **Natural Language Processing**: Processes user queries about builds, classes, and game mechanics
- **Knowledge Base Integration**: Maintains game-specific knowledge about classes, spells, and optimal strategies
- **Contextual Recommendations**: Provides build suggestions based on user preferences and current meta

# External Dependencies

## Core Libraries
- **Rich**: Terminal formatting and visual components for modern command-line experience
- **prompt_toolkit**: Advanced interactive CLI with live autocompletion and input handling
- **rapidfuzz**: High-performance fuzzy string matching for intelligent item search
- **BeautifulSoup4**: HTML parsing for ability extraction from uploaded files
- **Flask**: Web application framework for browser-based interface
- **itertools**: Built-in Python library for efficient combination generation during build creation

## AI Integration
- **OpenAI API**: GPT integration for intelligent build recommendations and natural language query processing
- **requests**: HTTP client for API communications and data fetching

## Data Sources
- **Wynnbuilder GitHub Repository**: Primary source for up-to-date item data (items.json)
- **Custom Class Database**: Internal JSON configuration for class mechanics and spell calculations

## Web Interface Dependencies
- **Bootstrap 5**: Frontend CSS framework for responsive design
- **Font Awesome**: Icon library for enhanced visual interface
- **JavaScript**: Client-side interactivity and AJAX communication

## Development Tools
- **pathlib**: Cross-platform file path handling
- **json**: Item data parsing and configuration management
- **threading**: Concurrent processing for web server and background tasks