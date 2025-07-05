import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageDraw

import argparse
import map_generator as mg


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
        ttk.Button(self.toolbar, text="Generate Map", command=self.generate_map).pack(fill=tk.X, pady=5)
        ttk.Button(self.toolbar, text="Save", command=self.save_image).pack(fill=tk.X, pady=10)

        self.shapes = []
        self.start_x = None
        self.start_y = None
        self.temp_shape = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

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
        self.shapes.append((elem, coords))
        self.temp_shape = None

    def save_image(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if not path:
            return
        img = Image.new("RGB", (self.width, self.height), mg.BG_COLOR)
        draw = ImageDraw.Draw(img)
        for elem, coords in self.shapes:
            if elem == "road":
                draw.line(coords, fill=mg.SHAPE_COLOR, width=3)
            elif elem == "wall":
                draw.line(coords, fill=mg.SHAPE_COLOR, width=5)
            elif elem == "river":
                draw.line(coords, fill="blue", width=4)
            elif elem == "district":
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
        self.shapes.clear()
        data = mg.generate_map_data(
            self.width,
            self.height,
            num_shapes=10,
            num_districts=self.district_var.get(),
        )
        for box in data["districts"]:
            self.canvas.create_rectangle(box, outline="gray", width=2)
            self.shapes.append(("district", box))
        for shape_type, shape_data in data["buildings"]:
            if shape_type == "polygon":
                self.canvas.create_polygon(shape_data, fill=mg.SHAPE_COLOR)
                self.shapes.append(("polygon", shape_data))
            else:
                if shape_type == "l":
                    box = shape_data
                else:
                    box = shape_data
                self.canvas.create_rectangle(box, outline=mg.SHAPE_COLOR)
                self.shapes.append((shape_type, box))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch the map editor")
    parser.add_argument("--width", type=int, default=mg.DEFAULT_WIDTH, help="canvas width")
    parser.add_argument("--height", type=int, default=mg.DEFAULT_HEIGHT, help="canvas height")
    parser.add_argument("--preset", choices=["1080p", "4k", "8k"], help="resolution preset")
    args = parser.parse_args()

    if args.preset:
        args.width, args.height = mg.RESOLUTION_PRESETS[args.preset]
    if not mg.validate_resolution(args.width, args.height):
        parser.error(f"Resolution must be within 1x1 and {mg.MAX_WIDTH}x{mg.MAX_HEIGHT}")

    app = MapEditor(width=args.width, height=args.height)
    app.mainloop()
