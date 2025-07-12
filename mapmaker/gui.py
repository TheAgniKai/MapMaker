import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageDraw

import argparse
import random
from . import generator as mg


class MapEditor(tk.Tk):
    def __init__(self, width=mg.DEFAULT_WIDTH, height=mg.DEFAULT_HEIGHT):
        super().__init__()
        self.title("MapMaker GUI Editor")
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg=mg.BG_COLOR)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.toolbar = ttk.Frame(self)
        self.toolbar.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(self.toolbar, text="Resolution").pack()
        self.res_var = tk.StringVar(value="Custom")
        presets = ["Custom"] + list(mg.RESOLUTION_PRESETS.keys())
        self.res_menu = ttk.OptionMenu(self.toolbar, self.res_var, self.res_var.get(), *presets, command=self.on_resolution_select)
        self.res_menu.pack(fill=tk.X)

        ttk.Label(self.toolbar, text="Districts").pack(pady=(5, 0))
        self.district_var = tk.IntVar(value=0)
        ttk.Spinbox(self.toolbar, from_=0, to=20, textvariable=self.district_var, width=5).pack(fill=tk.X)

        self.element = tk.StringVar(value="rectangle")
        options = [
            ("Rectangle Building", "rectangle"),
            ("Square Building", "square"),
            ("L Building", "l"),
            ("Polygon Building", "polygon"),
            ("Road", "road"),
            ("Wall", "wall"),
            ("River", "river"),
            ("District", "district"),
        ]
        for text, value in options:
            ttk.Radiobutton(self.toolbar, text=text, variable=self.element, value=value).pack(anchor=tk.W)
        self.political_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.toolbar,
            text="Political View",
            variable=self.political_var,
            command=self.render_canvas,
        ).pack(anchor=tk.W, pady=(5, 5))

        ttk.Button(self.toolbar, text="Generate Map", command=self.generate_map).pack(fill=tk.X, pady=5)
        ttk.Button(self.toolbar, text="Save", command=self.save_image).pack(fill=tk.X, pady=10)

        self.shapes = []  # list of shape dictionaries
        self.start_x = None
        self.start_y = None
        self.temp_shape = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def render_canvas(self):
        """Redraw all shapes according to the current political view setting."""
        self.canvas.delete("all")
        for shape in self.shapes:
            self._draw_shape(shape)

    def _draw_shape(self, shape):
        elem = shape["type"]
        coords = shape["coords"]
        if elem == "road":
            self.canvas.create_line(coords, fill=mg.SHAPE_COLOR, width=3)
        elif elem == "wall":
            if isinstance(coords[0], (tuple, list)):
                pts = coords + [coords[0]]
                self.canvas.create_line(pts, fill=mg.SHAPE_COLOR, width=5)
            else:
                self.canvas.create_line(coords, fill=mg.SHAPE_COLOR, width=5)
        elif elem == "river":
            self.canvas.create_line(coords, fill="blue", width=4)
        elif elem == "district":
            if isinstance(coords[0], (tuple, list)):
                if self.political_var.get() and "color" in shape:
                    self.canvas.create_polygon(
                        coords, outline="gray", fill=shape["color"], width=2
                    )
                else:
                    self.canvas.create_polygon(coords, outline="gray", width=2)
            else:
                if self.political_var.get() and "color" in shape:
                    self.canvas.create_rectangle(
                        coords, outline="gray", fill=shape["color"], width=2
                    )
                else:
                    self.canvas.create_rectangle(coords, outline="gray", width=2)
        elif elem == "polygon":
            if isinstance(coords[0], (tuple, list)):
                self.canvas.create_polygon(coords, fill=mg.SHAPE_COLOR)
            else:
                x1, y1, x2, y2 = coords
                box = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                poly = mg.random_polygon_from_box(box)
                self.canvas.create_polygon(poly, fill=mg.SHAPE_COLOR)
        else:
            x1, y1, x2, y2 = coords
            if elem == "square":
                side = min(abs(x2 - x1), abs(y2 - y1))
                x2 = x1 + side if x2 > x1 else x1 - side
                y2 = y1 + side if y2 > y1 else y1 - side
            box = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
            self.canvas.create_rectangle(box, outline=mg.SHAPE_COLOR)

    def on_resolution_select(self, value):
        if value in mg.RESOLUTION_PRESETS:
            w, h = mg.RESOLUTION_PRESETS[value]
            if mg.validate_resolution(w, h):
                self.width = w
                self.height = h
                self.canvas.config(width=w, height=h)
        self.res_var.set(value)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        elem = self.element.get()
        if elem in ("rectangle", "square", "l", "polygon", "district"):
            self.temp_shape = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline=mg.SHAPE_COLOR)
        else:
            self.temp_shape = self.canvas.create_line(event.x, event.y, event.x, event.y, fill=mg.SHAPE_COLOR, width=3)

    def on_drag(self, event):
        if not self.temp_shape:
            return
        if self.element.get() in ("rectangle", "square", "l", "polygon", "district"):
            self.canvas.coords(self.temp_shape, self.start_x, self.start_y, event.x, event.y)
        else:
            self.canvas.coords(self.temp_shape, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        if not self.temp_shape:
            return
        elem = self.element.get()
        coords = (self.start_x, self.start_y, event.x, event.y)
        shape = {"type": elem, "coords": coords}
        if elem == "district":
            shape["color"] = random.choice(mg.DISTRICT_COLORS)
        self.shapes.append(shape)
        self.temp_shape = None
        self.render_canvas()

    def save_image(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if not path:
            return
        img = Image.new("RGB", (self.width, self.height), mg.BG_COLOR)
        draw = ImageDraw.Draw(img)
        for shape in self.shapes:
            elem = shape["type"]
            coords = shape["coords"]
            if elem == "road":
                draw.line(coords, fill=mg.SHAPE_COLOR, width=3)
            elif elem == "wall":
                if isinstance(coords[0], (tuple, list)):
                    pts = coords + [coords[0]]
                    draw.line(pts, fill=mg.SHAPE_COLOR, width=5)
                else:
                    draw.line(coords, fill=mg.SHAPE_COLOR, width=5)
            elif elem == "river":
                draw.line(coords, fill="blue", width=4)
            elif elem == "district":
                if isinstance(coords[0], (tuple, list)):
                    if self.political_var.get() and "color" in shape:
                        draw.polygon(coords, outline="gray", fill=shape["color"], width=2)
                    else:
                        draw.polygon(coords, outline="gray", width=2)
                else:
                    if self.political_var.get() and "color" in shape:
                        draw.rectangle(
                            coords, outline="gray", fill=shape["color"], width=2
                        )
                    else:
                        draw.rectangle(coords, outline="gray", width=2)
            else:
                x1, y1, x2, y2 = coords
                if elem == "square":
                    side = min(abs(x2 - x1), abs(y2 - y1))
                    x2 = x1 + side if x2 > x1 else x1 - side
                    y2 = y1 + side if y2 > y1 else y1 - side
                    box = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                    draw.rectangle(box, fill=mg.SHAPE_COLOR)
                elif elem == "rectangle":
                    box = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                    draw.rectangle(box, fill=mg.SHAPE_COLOR)
                elif elem == "l":
                    box = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                    mg.draw_l_shape(draw, box)
                elif elem == "polygon":
                    box = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                    poly = mg.random_polygon_from_box(box)
                    mg.draw_polygon(draw, poly)
        img.save(path)

    def generate_map(self):
        self.canvas.delete("all")
        road_points = []
        original_roads = []
        for shape in self.shapes:
            if shape["type"] == "road":
                x1, y1, x2, y2 = shape["coords"]
                road_points.append((x1, y1))
                road_points.append((x2, y2))
                original_roads.append(shape)
        self.shapes.clear()
        data = mg.generate_map_data(
            self.width,
            self.height,
            num_shapes=10,
            num_districts=self.district_var.get(),
            num_walls=1,
            road_points=road_points,
        )
        for dist in data["districts"]:
            shape = {"type": "district", "coords": dist["poly"], "color": dist["color"]}
            self.shapes.append(shape)
        for wall in data["walls"]:
            shape = {"type": "wall", "coords": wall}
            self.shapes.append(shape)
        self.shapes.extend(original_roads)
        for line in data["roads"]:
            shape = {"type": "road", "coords": line}
            self.shapes.append(shape)
        for shape_type, shape_data in data["buildings"]:
            if shape_type == "polygon":
                shape = {"type": "polygon", "coords": shape_data}
            else:
                shape = {"type": shape_type, "coords": shape_data}
            self.shapes.append(shape)
        self.render_canvas()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Launch the map editor")
    parser.add_argument("--width", type=int, default=mg.DEFAULT_WIDTH, help="canvas width")
    parser.add_argument("--height", type=int, default=mg.DEFAULT_HEIGHT, help="canvas height")
    parser.add_argument("--preset", choices=["1080p", "4k", "8k"], help="resolution preset")
    args = parser.parse_args(argv)

    if args.preset:
        args.width, args.height = mg.RESOLUTION_PRESETS[args.preset]
    if not mg.validate_resolution(args.width, args.height):
        parser.error(f"Resolution must be within 1x1 and {mg.MAX_WIDTH}x{mg.MAX_HEIGHT}")

    app = MapEditor(width=args.width, height=args.height)
    app.mainloop()


if __name__ == "__main__":
    main()
