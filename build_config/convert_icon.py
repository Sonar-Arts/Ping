from PIL import Image
import os

def convert_to_ico():
    """Convert PNG icon to ICO format."""
    png_path = "../Ping Assets/Images/Icons/Ping Game Icon.png"
    ico_path = "../Ping Assets/Images/Icons/Ping Game Icon.ico"
    
    # Check if PNG exists
    if not os.path.exists(png_path):
        print(f"Error: Source icon not found at {png_path}")
        return False
    
    try:
        # Open PNG and create ICO with multiple sizes
        img = Image.open(png_path)
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        # Create ICO with multiple sizes
        icon_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128)]
        img.save(ico_path, format='ICO', sizes=icon_sizes)
        print(f"Successfully created ICO file at {ico_path}")
        return True
    except Exception as e:
        print(f"Error converting icon: {e}")
        return False

if __name__ == "__main__":
    convert_to_ico()