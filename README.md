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

The project is still under development, but a typical command to generate a map with a custom size might look like:

```bash
python map_generator.py --width 1200 --height 800 --output sample_map.png
```

You can also use resolution presets (1080p, 4k, 8k) or generate districts:

```bash
python map_generator.py --preset 4k --districts 3 --output big_map.png
```

This would produce a map saved as `sample_map.png` in the current directory.

## Generating a Sample Map

Once the generator script is implemented, you can create a quick sample map with default settings using:

```bash
python map_generator.py --output sample_map.png
```

Check the generated image file to view the result.

## GUI Editor

An experimental GUI editor is available for interactive map creation. Launch it with optional width and height parameters:

```bash
python gui_editor.py --width 1200 --height 800
```

Use the toolbar on the right to choose between buildings, roads, rivers, and districts. A drop-down lets you pick a resolution preset and how many districts to generate. Press **Generate Map** to fill the canvas automatically, then refine the result manually. Press **Save** to export your map to a PNG file.


