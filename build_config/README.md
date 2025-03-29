# Ping Game Build System

This directory contains the tools needed to build a standalone executable of the Ping game with proper icons and resources.

## Prerequisites

1. Python 3.8 or higher
2. pip (Python package manager)
3. The requirements specified in `build_requirements.txt`

## Installation

Install the required build dependencies:

```bash
pip install -r build_requirements.txt
```

## Building the Game

1. Make sure you're in the `build_config` directory:
```bash
cd build_config
```

2. Run the build script:
```bash
python build.py
```

The build process will:
- Convert the PNG icon to ICO format with multiple sizes for Windows
- Create a standalone executable with all required resources
- Package everything into a single executable file

## Output

After a successful build, you'll find:
- The executable at `dist/Ping.exe`
- The ICO file at `../Ping Assets/Images/Icons/Ping Game Icon.ico`

## Troubleshooting

If the build fails:
1. Check that all required packages are installed
2. Ensure the PNG icon file exists at the correct path
3. Check the error messages in the console output
4. Make sure all game resources are in their correct locations

## Clean Build

To perform a clean build:
- Delete the `build` and `dist` directories (the build script will do this automatically)
- Run the build script again

## Notes

- The executable will use the custom icon for both the window and taskbar
- All game resources (images, sounds, etc.) will be included in the executable
- The game will run without requiring Python installation