"""
Artemis Editor - File Handler Module

This module is responsible for loading and saving level data
in the .PMF (Ping Map File) format, which is based on JSON.
"""
import json
import os # Need os to ensure directory exists

# Placeholder for future file handling functions
# print("Artemis Modules/artemis_file_handler.py loaded (placeholder)") # Removed placeholder print

def load_pmf(filepath):
    """
    Loads level data from a .PMF file.
    Returns the loaded data dictionary or None if an error occurs.
    """
    print(f"Attempting to load PMF: {filepath}")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        print(f"Successfully loaded data from {filepath}")

        # --- Merge sprites back into objects post-load ---
        if data and isinstance(data, dict) and 'objects' in data and 'sprites' in data:
             if isinstance(data['objects'], list) and isinstance(data['sprites'], list):
                  print(f"Found 'sprites' list ({len(data['sprites'])} items), merging into 'objects'.")
                  data['objects'].extend(data['sprites'])
                  del data['sprites'] # Remove the separate list after merge
             else:
                  print("Warning: 'objects' or 'sprites' key found but is not a list. Skipping merge.")

        return data
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in file - {filepath}. Details: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading {filepath}: {e}")
        return None

def save_pmf(filepath, level_data):
    """
    Saves level data to a .PMF file.
    Ensures the directory exists before saving.
    """
    try:
        # Ensure the target directory exists
        target_dir = os.path.dirname(filepath)
        if target_dir and not os.path.exists(target_dir): # Check if target_dir is not empty
            os.makedirs(target_dir)
            print(f"Created directory: {target_dir}")

        # --- Separate sprites from objects before saving ---
        import copy # Need copy for deepcopy
        save_data = copy.deepcopy(level_data) # Work on a copy
        sprites = []
        other_objects = []

        if 'objects' in save_data and isinstance(save_data['objects'], list):
            for obj in save_data['objects']:
                if isinstance(obj, dict) and obj.get('type') == 'sprite':
                    sprites.append(obj)
                else:
                    other_objects.append(obj)

            save_data['objects'] = other_objects # Update objects list
            if sprites: # Only add 'sprites' key if there are any sprites
                save_data['sprites'] = sprites
                print(f"Separated {len(sprites)} sprites for saving.")
        else:
            print("No 'objects' list found in level_data or it's not a list.")
            # Ensure 'objects' exists, even if empty
            if 'objects' not in save_data:
                 save_data['objects'] = []


        # Write the potentially modified level data as JSON
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=4) # Use indent for readability
        print(f"Level data successfully saved to {filepath} (Sprites separated: {'yes' if sprites else 'no'})")
        return True
    except IOError as e:
        print(f"Error writing to file {filepath}: {e}")
        return False
    except TypeError as e:
        print(f"Error serializing level data to JSON: {e}")
        # This might happen if level_data contains non-serializable objects
        return False
    except Exception as e:
        print(f"An unexpected error occurred while saving {filepath}: {e}")
        return False

# You might add classes here later if the file handling becomes more complex