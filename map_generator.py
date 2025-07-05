import argparse
import random
import math
from PIL import Image, ImageDraw

# Default canvas size. These values can be overridden via command line
# arguments or when calling the drawing functions directly.
DEFAULT_WIDTH, DEFAULT_HEIGHT = 800, 600
MAX_WIDTH, MAX_HEIGHT = 8192, 8192

RESOLUTION_PRESETS = {
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
    "8k": (7680, 4320),
}

BG_COLOR = "white"
SHAPE_COLOR = "black"

# A palette of colors used for political districts
DISTRICT_COLORS = [
    "#f4aaaa",
    "#a8d5a2",
    "#a2b5d5",
    "#f4e2a2",
    "#e2a2f4",
    "#a2f4f4",
]


def intersects(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 <= bx1 or ax1 >= bx2 or ay2 <= by1 or ay1 >= by2)


def validate_resolution(width, height):
    """Return True if width and height are within supported range."""
    return 1 <= width <= MAX_WIDTH and 1 <= height <= MAX_HEIGHT


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


def polygon_bounds(points):
    """Return bounding box for a list of points."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def generate_irregular_polygon(cx, cy, avg_radius, irregularity=0.3, spikeyness=0.2, num_vertices=8):
    """Generate an irregular polygon around a center point."""
    irregularity = max(0, min(irregularity, 1)) * 2 * math.pi / num_vertices
    spikeyness = max(0, min(spikeyness, 1)) * avg_radius

    angle_steps = []
    lower = (2 * math.pi / num_vertices) - irregularity
    upper = (2 * math.pi / num_vertices) + irregularity
    sum_steps = 0
    for _ in range(num_vertices):
        step = random.uniform(lower, upper)
        angle_steps.append(step)
        sum_steps += step
    k = sum_steps / (2 * math.pi)
    angle_steps = [step / k for step in angle_steps]

    points = []
    angle = random.uniform(0, 2 * math.pi)
    for step in angle_steps:
        r = max(5, random.gauss(avg_radius, spikeyness))
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((int(x), int(y)))
        angle += step
    return points


def generate_districts(width, height, count, max_attempts=1000):
    """Generate irregular district polygons that do not overlap."""
    districts = []
    boxes = []
    attempts = 0
    while len(districts) < count and attempts < max_attempts:
        radius = random.randint(min(width, height) // 8, min(width, height) // 3)
        cx = random.randint(radius, width - radius)
        cy = random.randint(radius, height - radius)
        poly = generate_irregular_polygon(cx, cy, radius)
        box = polygon_bounds(poly)
        if any(intersects(box, b) for b in boxes):
            attempts += 1
            continue
        boxes.append(box)
        districts.append({"poly": poly, "color": random.choice(DISTRICT_COLORS)})
    return districts


def generate_walls(width, height, count=1):
    """Generate one or more irregular wall polygons around the map."""
    walls = []
    margin = min(width, height) // 15
    cx, cy = width // 2, height // 2
    for i in range(count):
        radius = min(width, height) // 2 - margin - i * (margin // 2)
        wall = generate_irregular_polygon(
            cx,
            cy,
            radius,
            irregularity=0.1 + 0.05 * i,
            spikeyness=0.05,
            num_vertices=12,
        )
        walls.append(wall)
    return walls


def generate_map_data(width, height, num_shapes=10, num_districts=0, num_walls=1):
    return {
        "buildings": generate_buildings(width, height, num_shapes),
        "roads": [],
        "rivers": [],
        "districts": generate_districts(width, height, num_districts) if num_districts > 0 else [],
        "walls": generate_walls(width, height, num_walls) if num_walls > 0 else [],
    }


def draw_map(
    filename="map.png",
    width=DEFAULT_WIDTH,
    height=DEFAULT_HEIGHT,
    num_shapes=10,
    num_districts=0,
    num_walls=1,
):
    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    data = generate_map_data(width, height, num_shapes, num_districts, num_walls)
    for shape_type, shape_data in data["buildings"]:
        if shape_type == "l":
            draw_l_shape(draw, shape_data)
        elif shape_type == "polygon":
            draw_polygon(draw, shape_data)
        else:
            draw.rectangle(shape_data, fill=SHAPE_COLOR)
    for district in data["districts"]:
        color = district["color"]
        poly = district["poly"]
        draw.polygon(poly, outline="gray", fill=color, width=2)
    for wall in data["walls"]:
        pts = wall + [wall[0]]
        draw.line(pts, fill=SHAPE_COLOR, width=5)
    img.save(filename)
    print(f"Map saved to {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a procedural map")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help="map width")
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT, help="map height")
    parser.add_argument("--preset", choices=sorted(RESOLUTION_PRESETS.keys()), help="use a resolution preset")
    parser.add_argument("--num-shapes", type=int, default=10, help="number of buildings")
    parser.add_argument("--districts", type=int, default=0, help="number of districts to generate")
    parser.add_argument("--walls", type=int, default=1, help="number of wall layers")
    parser.add_argument("--output", type=str, default="map.png", help="output image path")
    args = parser.parse_args()

    if args.preset:
        args.width, args.height = RESOLUTION_PRESETS[args.preset]
    if not validate_resolution(args.width, args.height):
        parser.error(f"Resolution must be within 1x1 and {MAX_WIDTH}x{MAX_HEIGHT}")

    draw_map(
        filename=args.output,
        width=args.width,
        height=args.height,
        num_shapes=args.num_shapes,
        num_districts=args.districts,
        num_walls=args.walls,
    )
