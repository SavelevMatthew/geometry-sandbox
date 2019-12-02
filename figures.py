class Figure():
    def __init__(self, name, verts, edges, faces, center=(0, 0, 0)):
        self.name = name
        self.vertices = verts
        self.edges = edges
        self.center = center
        self.faces = faces

    def move(self, dx, dy, dz):
        new_verts = []
        for vert in self.vertices:
            unlocked = list(vert)
            unlocked[0] += dx
            unlocked[1] += dy
            unlocked[2] += dz
            new_verts.append(tuple(unlocked))
        self.vertices = tuple(new_verts)


class Cube(Figure):
    vertices = (-10.0, -10.0, -10.0), (10.0, -10.0, -10.0), \
               (10.0, 10.0, -10.0), (-10.0, 10.0, -10.0), \
               (-10.0, -10.0, 10.0), (10.0, -10.0, 10.0), \
               (10.0, 10.0, 10.0), (-10.0, 10.0, 10.0)
    edges = (0, 1), (1, 2), (2, 3), (3, 0), \
            (4, 5), (5, 6), (6, 7), (7, 4), \
            (0, 4), (1, 5), (2, 6), (3, 7)
    faces = (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), \
            (2, 3, 7, 6), (0, 3, 7, 4), (1, 2, 6, 5)

    def __init__(self, name):
        super().__init__(name, Cube.vertices, Cube.edges, Cube.faces)
