
import json
import os

def load_items():
    """Loads items from the items.json file."""
    # Construct the absolute path to the items.json file
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'items.json')
    
    try:
        with open(file_path, 'r') as f:
            # Load the JSON data and filter out items without the 'name' key
            return [item for item in json.load(f) if 'name' in item]
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}.")
        return None
