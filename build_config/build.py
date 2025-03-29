import os
import sys
import shutil
import subprocess
from convert_icon import convert_to_ico

def build_game():
    """Build the game executable."""
    print("Starting Ping game build process...")
    
    # First, convert the icon
    print("\n1. Converting icon...")
    if not convert_to_ico():
        print("Failed to convert icon. Build process aborted.")
        return False
        
    # Clean previous build directories
    print("\n2. Cleaning previous builds...")
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"Cleaned {dir_name} directory")
            except Exception as e:
                print(f"Warning: Could not clean {dir_name}: {e}")
    
    # Run PyInstaller
    print("\n3. Building executable...")
    try:
        result = subprocess.run(['pyinstaller', 'ping.spec'], 
                              capture_output=True, 
                              text=True,
                              check=True)
        print("Build completed successfully!")
    except subprocess.CalledProcessError as e:
        print("Build failed!")
        print("Error output:")
        print(e.output)
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    
    # Verify the executable was created
    exe_path = os.path.join('dist', 'Ping.exe')
    if os.path.exists(exe_path):
        print(f"\nExecutable created successfully at: {exe_path}")
        return True
    else:
        print("\nError: Executable not found after build")
        return False

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    success = build_game()
    sys.exit(0 if success else 1)