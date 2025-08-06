"""
Web interface for Wynncraft Item Builder CLI Tool
Flask-based web application providing browser access to build generation
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import sys
from pathlib import Path
import threading
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import loader, builder, filters, stats
from export import export_to_wynnbuilder, export_build_to_text
from ai_agent import WynnAI
from rich.console import Console

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'wynnbuilder_secret_key_change_in_production')

# Initialize components
console = Console()
ai_agent = WynnAI()
items_cache = None
items_cache_time = 0

def load_items_cache():
    """Load items into cache if not already loaded or if cache is old."""
    global items_cache, items_cache_time
    
    current_time = time.time()
    
    # Reload cache every 30 minutes or if not loaded
    if items_cache is None or (current_time - items_cache_time) > 1800:
        try:
            items_data = loader.load_items()
            if items_data:
                items_cache = items_data.get('items', [])
                items_cache_time = current_time
                return True
        except Exception as e:
            console.print(f"[red]Error loading items: {e}[/red]")
            return False
    
    return items_cache is not None

@app.route('/')
def index():
    """Main page."""
    if not load_items_cache():
        return render_template('index.html', error="Could not load item data. Please ensure items.json is available.")
    
    return render_template('index.html', items_count=len(items_cache) if items_cache else 0)

@app.route('/api/generate_builds', methods=['POST'])
def api_generate_builds():
    """API endpoint for generating builds."""
    try:
        if not load_items_cache():
            return jsonify({'error': 'Item data not available'}), 500
        
        data = request.get_json()
        
        # Extract parameters
        class_choice = data.get('class', 'mage')
        playstyle = data.get('playstyle', 'spellspam')
        elements = data.get('elements', ['thunder'])
        no_mythics = data.get('no_mythics', False)
        min_dps = data.get('min_dps', 0)
        min_mana = data.get('min_mana', 0)
        max_cost = data.get('max_cost', 0)
        
        # Prepare filters
        build_filters = {
            'min_dps': min_dps,
            'min_mana_regen': min_mana,
            'max_cost': max_cost if max_cost > 0 else None,
            'no_mythics': no_mythics
        }
        
        # Filter items
        filtered_items = filters.filter_items(
            items_cache,
            class_filter=class_choice,
            playstyle_filter=playstyle,
            no_mythics=no_mythics
        )
        
        # Generate builds
        builds = builder.generate_builds(
            filtered_items,
            class_choice,
            playstyle,
            elements,
            build_filters,
            max_builds=20  # Limit for web interface
        )
        
        # Calculate stats for each build
        build_results = []
        for i, build in enumerate(builds[:10]):  # Top 10 for display
            build_stats = builder.calculate_build_stats(build)
            
            # Format build for JSON response
            build_data = {
                'id': i + 1,
                'class': class_choice,
                'items': {},
                'stats': {
                    'dps': round(build_stats['dps'], 1),
                    'mana': round(build_stats['mana'], 2),
                    'ehp': round(build_stats['ehp'], 0),
                    'cost': round(build_stats['cost'], 0)
                },
                'skill_points': build_stats['skill_points']
            }
            
            # Add items with details
            item_slots = ['weapon', 'helmet', 'chestplate', 'leggings', 'boots', 'ring1', 'ring2', 'bracelet', 'necklace']
            for slot in item_slots:
                if slot in build:
                    item = build[slot]
                    build_data['items'][slot] = {
                        'name': item.get('name', ''),
                        'tier': item.get('tier', 'Normal'),
                        'type': item.get('type', ''),
                        'level': item.get('lvl', 0)
                    }
            
            build_results.append(build_data)
        
        return jsonify({
            'success': True,
            'builds': build_results,
            'total_found': len(builds)
        })
        
    except Exception as e:
        console.print(f"[red]Error generating builds: {e}[/red]")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai_query', methods=['POST'])
def api_ai_query():
    """API endpoint for AI assistant queries."""
    try:
        if not load_items_cache():
            return jsonify({'error': 'Item data not available'}), 500
        
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Process query with AI agent
        response = ai_agent.process_query(query, items_cache)
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        console.print(f"[red]Error processing AI query: {e}[/red]")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export_build', methods=['POST'])
def api_export_build():
    """API endpoint for exporting builds."""
    try:
        data = request.get_json()
        build_data = data.get('build')
        export_format = data.get('format', 'wynnbuilder')
        
        if not build_data:
            return jsonify({'error': 'No build data provided'}), 400
        
        class_name = build_data.get('class', 'mage')
        
        # Create build list for export
        build_list = [class_name.title()]
        item_slots = ['weapon', 'helmet', 'chestplate', 'leggings', 'boots', 'ring1', 'ring2', 'bracelet', 'necklace']
        
        for slot in item_slots:
            item_name = ''
            if slot in build_data.get('items', {}):
                item_name = build_data['items'][slot].get('name', '')
            build_list.append(item_name)
        
        if export_format == 'wynnbuilder':
            export_string = export_to_wynnbuilder(build_list)
            return jsonify({
                'success': True,
                'export_string': export_string,
                'format': 'wynnbuilder'
            })
        
        elif export_format == 'text':
            # Create a mock build object for text export
            mock_build = {
                'class': class_name,
                **{slot: {'name': build_data['items'].get(slot, {}).get('name', '')} 
                   for slot in item_slots if slot in build_data.get('items', {})}
            }
            
            text_export = export_build_to_text(
                mock_build,
                build_data.get('stats', {}),
                class_name
            )
            
            return jsonify({
                'success': True,
                'export_text': text_export,
                'format': 'text'
            })
        
        else:
            return jsonify({'error': 'Unsupported export format'}), 400
            
    except Exception as e:
        console.print(f"[red]Error exporting build: {e}[/red]")
        return jsonify({'error': str(e)}), 500

@app.route('/api/items_summary')
def api_items_summary():
    """API endpoint for items summary."""
    try:
        if not load_items_cache():
            return jsonify({'error': 'Item data not available'}), 500
        
        summary = loader.get_items_summary(items_cache)
        return jsonify(summary)
        
    except Exception as e:
        console.print(f"[red]Error getting items summary: {e}[/red]")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'items_loaded': items_cache is not None,
        'items_count': len(items_cache) if items_cache else 0
    })

@app.errorhandler(404)
def not_found(error):
    """404 error handler."""
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler."""
    return render_template('index.html', error="Internal server error"), 500

def start_web_server():
    """Start the Flask web server."""
    try:
        # Load items cache on startup
        if not load_items_cache():
            console.print("[yellow]Warning: Could not load items on startup[/yellow]")
        
        console.print("[green]Starting web server on http://0.0.0.0:5000[/green]")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        
    except Exception as e:
        console.print(f"[red]Error starting web server: {e}[/red]")
        raise

if __name__ == '__main__':
    start_web_server()
