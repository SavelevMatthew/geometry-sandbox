import figures
import camera
from math import sin, cos
from numpy import matrix, dot


class Engine():
    def __init__(self, cam):
        self.figures = {}
        self.cam = cam

    def add_object(self, obj):
        self.figures[obj.name] = obj

    def generate_name(self, prefix):
        i = 1
        str = '{0} {1}'.format(prefix, i)
        while str in self.figures:
            i += 1
            str = '{0} {1}'.format(prefix, i)
        return str

    def delete_item(self, name):
        if name in self.figures:
            del self.figures[name]

    @staticmethod
    def rotate2d(pos, radian):
        x, y = pos
        s, c = sin(radian), cos(radian)
        return x * c - y * s, y * c + x * s

    @staticmethod
    def rotate_vert(v, ax, ay, az):
        sx, cx = sin(ax), cos(ax)
        sy, cy = sin(ay), cos(ay)
        sz, cz = sin(az), cos(az)
        rot_x = matrix([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
        rot_y = matrix([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        rot_z = matrix([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
        tr = matrix('{0}; {1}; {2}'.format(v[0], v[1], v[2]))
        x_rot = rot_x.dot(tr)
        y_rot = rot_y.dot(x_rot)
        z_rot = rot_z.dot(y_rot)
        listed = z_rot.tolist()
        for coord in listed:
            yield coord[0]
