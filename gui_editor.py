import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageDraw

import map_generator as mg


class MapEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MapMaker GUI Editor")
        self.canvas = tk.Canvas(self, width=mg.WIDTH, height=mg.HEIGHT, bg=mg.BG_COLOR)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.toolbar = ttk.Frame(self)
        self.toolbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.element = tk.StringVar(value="rectangle")
        options = [
            ("Rectangle Building", "rectangle"),
            ("Square Building", "square"),
            ("L Building", "l"),
            ("Road", "road"),
            ("Wall", "wall"),
        ]
        for text, value in options:
            ttk.Radiobutton(self.toolbar, text=text, variable=self.element, value=value).pack(anchor=tk.W)
        ttk.Button(self.toolbar, text="Save", command=self.save_image).pack(fill=tk.X, pady=10)

        self.shapes = []
        self.start_x = None
        self.start_y = None
        self.temp_shape = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        elem = self.element.get()
        if elem in ("rectangle", "square", "l"):
            self.temp_shape = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline=mg.SHAPE_COLOR)
        else:
            self.temp_shape = self.canvas.create_line(event.x, event.y, event.x, event.y, fill=mg.SHAPE_COLOR, width=3)

    def on_drag(self, event):
        if not self.temp_shape:
            return
        if self.element.get() in ("rectangle", "square", "l"):
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
        img = Image.new("RGB", (mg.WIDTH, mg.HEIGHT), mg.BG_COLOR)
        draw = ImageDraw.Draw(img)
        for elem, coords in self.shapes:
            if elem == "road":
                draw.line(coords, fill=mg.SHAPE_COLOR, width=3)
            elif elem == "wall":
                draw.line(coords, fill=mg.SHAPE_COLOR, width=5)
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
        img.save(path)


if __name__ == "__main__":
    app = MapEditor()
    app.mainloop()
