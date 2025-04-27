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

        # Write the level data as JSON
        with open(filepath, 'w') as f:
            json.dump(level_data, f, indent=4) # Use indent for readability
        print(f"Level data successfully saved to {filepath}")
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