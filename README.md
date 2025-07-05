# MapMaker

MapMaker is a project aimed at creating a simple map generator for tabletop games and world-building. The goal is to produce procedural maps that can be saved as images for further editing or use.

## Project Goals

- Provide a lightweight map generator with configurable parameters.
- Offer an easy command-line interface to produce maps quickly.
- Serve as a foundation for experimentation with procedural generation techniques.

## Installation

1. Ensure you have **Python 3.8** or newer installed.
2. Clone this repository:

   ```bash
   git clone <repository-url>
   cd MapMaker
   ```
3. (Optional) Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies (once a `requirements.txt` file is available):

   ```bash
   pip install -r requirements.txt
   ```

## Usage Example

The project is still under development, but a typical command to generate a map might look like:

```bash
python generate_map.py --width 800 --height 600 --output sample_map.png
```

This would produce a map saved as `sample_map.png` in the current directory.

## Generating a Sample Map

Once the generator script is implemented, you can create a quick sample map with default settings using:

```bash
python generate_map.py --output sample_map.png
```

Check the generated image file to view the result.

## GUI Editor

An experimental GUI editor is available for interactive map creation. Launch it with:

```bash
python gui_editor.py
```

Use the toolbar on the right to choose between buildings, roads, and walls. Click
and drag on the canvas to place elements. Press **Save** to export your map to a
PNG file.


