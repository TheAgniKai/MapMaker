import argparse
import random
from PIL import Image, ImageDraw

# Default canvas size. These values can be overridden via command line
# arguments or when calling the drawing functions directly.
DEFAULT_WIDTH, DEFAULT_HEIGHT = 800, 600
BG_COLOR = "white"
SHAPE_COLOR = "black"


def intersects(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 <= bx1 or ax1 >= bx2 or ay2 <= by1 or ay1 >= by2)


def generate_buildings(width, height, num_shapes=10, max_attempts=1000):
    """Generate building shapes within the given canvas size."""
    shapes = []
    boxes = []
    for _ in range(num_shapes):
        for _ in range(max_attempts):
            shape_type = random.choice(["square", "rectangle", "l", "polygon"])
            if shape_type == "square":
                side = random.randint(20, 100)
                w = h = side
            else:
                w = random.randint(30, 120)
                h = random.randint(30, 120)
            x = random.randint(0, width - w)
            y = random.randint(0, height - h)
            box = (x, y, x + w, y + h)
            if any(intersects(box, b) for b in boxes):
                continue
            boxes.append(box)
            if shape_type == "polygon":
                poly = random_polygon_from_box(box)
                shapes.append((shape_type, poly))
            else:
                shapes.append((shape_type, box))
            break
    return shapes


def draw_l_shape(draw, box):
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1
    thickness = max(10, min(w, h) // 3)
    draw.rectangle([x1, y1, x1 + thickness, y2], fill=SHAPE_COLOR)
    draw.rectangle([x1, y1, x2, y1 + thickness], fill=SHAPE_COLOR)


def draw_polygon(draw, points):
    draw.polygon(points, fill=SHAPE_COLOR)


def random_polygon_from_box(box, min_vertices=3, max_vertices=6):
    """Create a random polygon that fits inside the given box."""
    x1, y1, x2, y2 = box
    points = []
    for _ in range(random.randint(min_vertices, max_vertices)):
        px = random.randint(x1, x2)
        py = random.randint(y1, y2)
        points.append((px, py))
    return points


def generate_map_data(width, height, num_shapes=10):
    return {
        "buildings": generate_buildings(width, height, num_shapes),
        "roads": [],
        "rivers": [],
        "districts": [],
        "walls": [],
    }


def draw_map(filename="map.png", width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, num_shapes=10):
    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    data = generate_map_data(width, height, num_shapes)
    for shape_type, shape_data in data["buildings"]:
        if shape_type == "l":
            draw_l_shape(draw, shape_data)
        elif shape_type == "polygon":
            draw_polygon(draw, shape_data)
        else:
            draw.rectangle(shape_data, fill=SHAPE_COLOR)
    img.save(filename)
    print(f"Map saved to {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a procedural map")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help="map width")
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT, help="map height")
    parser.add_argument("--num-shapes", type=int, default=10, help="number of buildings")
    parser.add_argument("--output", type=str, default="map.png", help="output image path")
    args = parser.parse_args()
    draw_map(filename=args.output, width=args.width, height=args.height, num_shapes=args.num_shapes)
