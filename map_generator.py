import random
from PIL import Image, ImageDraw

WIDTH, HEIGHT = 800, 600
BG_COLOR = "white"
SHAPE_COLOR = "black"


def intersects(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 <= bx1 or ax1 >= bx2 or ay2 <= by1 or ay1 >= by2)


def generate_buildings(num_shapes=10, max_attempts=1000):
    shapes = []
    boxes = []
    for _ in range(num_shapes):
        for _ in range(max_attempts):
            shape_type = random.choice(["square", "rectangle", "l"])
            if shape_type == "square":
                side = random.randint(20, 100)
                w = h = side
            else:
                w = random.randint(30, 120)
                h = random.randint(30, 120)
            x = random.randint(0, WIDTH - w)
            y = random.randint(0, HEIGHT - h)
            box = (x, y, x + w, y + h)
            if any(intersects(box, b) for b in boxes):
                continue
            boxes.append(box)
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


def draw_map(filename="map.png", num_shapes=10):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    shapes = generate_buildings(num_shapes)
    for shape_type, box in shapes:
        if shape_type == "l":
            draw_l_shape(draw, box)
        else:
            draw.rectangle(box, fill=SHAPE_COLOR)
    img.save(filename)
    print(f"Map saved to {filename}")


if __name__ == "__main__":
    draw_map()
