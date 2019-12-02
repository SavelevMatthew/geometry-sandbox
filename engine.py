import figures
import camera
import math


class Engine():
    def __init__(self):
        self.figures = {}
        self.cam = camera.Cam((0, 0, -50))

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
        s, c = math.sin(radian), math.cos(radian)
        return x * c - y * s, y * c + x * s
