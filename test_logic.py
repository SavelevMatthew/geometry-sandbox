import unittest
from math import pi
from engine import Engine
from figures import *
from camera import Cam


class TestFigure(unittest.TestCase):
    def test_rotate(self):
        verts = (0, 0, 0), (1, 0, 0)
        edges = (0, 1)
        fig = Figure('test', verts, edges)
        fig.rotate(90, 0, 0)
        self.assertEqual((1, 0, 0), fig.vertices[1])

    def test_scale(self):
        verts = (-1, -1, -1), (1, 1, 1)
        edges = (0, 1)
        fig = Figure('test', verts, edges)
        fig.scale(2, 3, 4)
        self.assertEqual((-2, -3, -4), fig.vertices[0])
        self.assertEqual((2, 3, 4), fig.vertices[1])

    def test_move(self):
        verts = (0, 0, 0), (1, 1, 1)
        edges = (0, 1)
        fig = Figure('test', verts, edges)
        fig.move(50, 60, 70)
        self.assertEqual((50, 60, 70), fig.vertices[0])

    def test_plane(self):
        plane = Plane('test', 4)
        self.assertEqual(len(plane.vertices), 4)

    def test_ball(self):
        precision = 4
        ball = Ball('test', precision)
        self.assertEqual(len(ball.vertices),
                         (precision - 1) * precision * 2 + 2)


class TestCamera(unittest.TestCase):
    def test_button_reaction(self):
        cam = Cam()
        keys = {'W': True, 'D': True, 'A': False, 'S': False, 'SPACE': True,
                'SHIFT': False}
        cam.update_position(100, keys)
        self.assertEqual(cam.pos, [50, -50, 50])
        keys = {'W': False, 'D': False, 'A': True, 'S': True, 'SPACE': False,
                'SHIFT': True}
        cam.update_position(50, keys)
        self.assertEqual(cam.pos, [25, -25, 25])

        cam = Cam()
        cam.mode = 1
        keys = {'W': True, 'D': True, 'A': False, 'S': False, 'SPACE': True,
                'SHIFT': False}
        cam.update_position(100, keys)
        self.assertEqual(cam.pos, [50, -50, 50])
        keys = {'W': False, 'D': False, 'A': True, 'S': True, 'SPACE': False,
                'SHIFT': True}
        cam.update_position(50, keys)
        self.assertEqual(cam.pos, [25, -25, 25])


class TestEngine(unittest.TestCase):
    def test_rotation(self):
        vert = (1, 0, 0)
        coord = []
        for c in Engine.rotate_vert(vert, 0, 0, pi / 2):
            coord.append(c)
        self.assertEqual(1, coord[1])

    def test_name_generator(self):
        prefix = 'test'
        eng = Engine(Cam())
        name = eng.generate_name(prefix)
        self.assertEqual(prefix + ' 1', name)
        eng.figures[prefix + ' 1'] = None
        name = eng.generate_name(prefix)
        self.assertEqual(prefix + ' 2', name)


if __name__ == '__main__':
    unittest.main()
