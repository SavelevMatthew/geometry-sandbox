from math import pi, cos, sin
from numpy import dot, matrix


class Figure():
    precise_depend = False

    def __init__(self, name, verts, edges, center=(0, 0, 0)):
        self.name = name
        self.vertices = verts
        self.edges = edges
        self.center = center

    def move(self, dx, dy, dz):
        new_verts = []
        for vert in self.vertices:
            unlocked = list(vert)
            unlocked[0] += dx
            unlocked[1] += dy
            unlocked[2] += dz
            new_verts.append(tuple(unlocked))
        self.vertices = tuple(new_verts)
        new_center = []
        new_center.append(self.center[0] + dx)
        new_center.append(self.center[1] + dy)
        new_center.append(self.center[2] + dz)
        self.center = tuple(new_center)

    def scale(self, kx, ky, kz):
        new_verts = []
        for vert in self.vertices:
            v = [vert[i] - self.center[i] for i in range(len(vert))]
            v[0] *= kx
            v[1] *= ky
            v[2] *= kz
            final_pos = [v[i] + self.center[i] for i in range(len(v))]
            new_verts.append(tuple(final_pos))
        self.vertices = tuple(new_verts)

    def rotate(self, ax, ay, az):
        radian_x = ax * pi / 180
        radian_y = ay * pi / 180
        radian_z = az * pi / 180
        sx, cx = sin(radian_x), cos(radian_x)
        sy, cy = sin(radian_y), cos(radian_y)
        sz, cz = sin(radian_z), cos(radian_z)
        rot_x = matrix([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
        rot_y = matrix([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        rot_z = matrix([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
        new_verts = []
        for vert in self.vertices:
            v = [vert[i] - self.center[i] for i in range(len(vert))]
            tr = matrix('{0}; {1}; {2}'.format(v[0], v[1], v[2]))
            x_rot = rot_x.dot(tr)
            y_rot = rot_y.dot(x_rot)
            z_rot = rot_z.dot(y_rot)
            listed = z_rot.tolist()
            final = [listed[i][0] + self.center[i] for i in range(len(listed))]
            new_verts.append(tuple(final))
        self.vertices = tuple(new_verts)


class Cube(Figure):
    vertices = (-10.0, -10.0, -10.0), (10.0, -10.0, -10.0), \
               (10.0, 10.0, -10.0), (-10.0, 10.0, -10.0), \
               (-10.0, -10.0, 10.0), (10.0, -10.0, 10.0), \
               (10.0, 10.0, 10.0), (-10.0, 10.0, 10.0)
    edges = (0, 1), (1, 2), (2, 3), (3, 0), \
            (4, 5), (5, 6), (6, 7), (7, 4), \
            (0, 4), (1, 5), (2, 6), (3, 7)

    def __init__(self, name):
        super().__init__(name, Cube.vertices, Cube.edges)


class Plane(Figure):
    precise_depend = True

    def __init__(self, name, precision):
        r = 10 * (2**(0.5))
        step = 2 * pi / precision
        angle = (step + pi) / 2
        verts = []
        edges = []
        prev = None
        for i in range(precision):
            x, y = r * cos(angle), r * sin(angle)
            verts.append((x, y, 0))
            angle += step
            if prev is not None:
                edges.append((prev, i))
            prev = i
        edges.append((edges[len(edges) - 1][1], 0))

        super().__init__(name, tuple(verts), tuple(edges))


class Circle(Figure):
    precise_depend = True

    def __init__(self, name, precision):
        edges = []
        verts = []

        r = 10
        z_step = pi / precision
        raw_verts = []
        verts.append((0, 0, r))
        for layer in range(1, precision):
            z = cos(z_step * layer) * r
            layer_r = sin(z_step * layer) * r
            layer_verts = []
            step = pi / precision
            angle = (step + pi) / 2
            for i in range(precision * 2):
                x, y = layer_r * cos(angle), layer_r * sin(angle)
                layer_verts.append((x, y, z))
                verts.append((x, y, z))
                angle += step
            raw_verts.append(layer_verts)
        verts.append((0, 0, -r))

        counter = 1
        for j in range(1, 2 * precision * (precision - 1) + 1):
            edges.append((max(0, j - 2 * precision), j))
        for j in range((precision - 2) * 2 * precision + 1,
                       (precision - 1) * 2 * precision + 1):
            edges.append((j, (precision - 1) * 2 * precision + 1))
        for j in range(1, precision):
            start = 1 + (j - 1) * 2 * precision
            for i in range(2 * precision - 1):
                edges.append((start + i, start + i + 1))
            edges.append((start, start + 2 * precision - 1))
            start += j * precision * 2

        super().__init__(name, tuple(verts), tuple(edges))
