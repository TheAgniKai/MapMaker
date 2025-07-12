import numpy as np
from scipy.spatial import Voronoi


def generate_road_network(points, width, height):
    """Generate roads using a Voronoi diagram of the given points."""
    vor = Voronoi(points)
    lines = []
    for vpair in vor.ridge_vertices:
        if -1 in vpair:
            continue
        p1 = vor.vertices[vpair[0]]
        p2 = vor.vertices[vpair[1]]
        if 0 <= p1[0] <= width and 0 <= p1[1] <= height and 0 <= p2[0] <= width and 0 <= p2[1] <= height:
            lines.append((int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1])))
    return lines

