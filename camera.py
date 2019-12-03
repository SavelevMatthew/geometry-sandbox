import math


class Cam:
    def __init__(self, pos=(0, 0, 0), rot=(0, 0)):
        self.pos = list(pos)
        self.rot = list(rot)
        self.sensitivity = 500

    def update_position(self, dt, keys):
        s = dt / 2
        x, y = s * math.sin(self.rot[1]), s * math.cos(self.rot[1])

        if keys['W']:
            self.pos[0] += x
            self.pos[2] += y
        if keys['S']:
            self.pos[0] -= x
            self.pos[2] -= y
        if keys['A']:
            self.pos[0] -= y
            self.pos[2] += x
        if keys['D']:
            self.pos[0] += y
            self.pos[2] -= x
        if keys['SPACE']:
            self.pos[1] -= s
        if keys['SHIFT']:
            self.pos[1] += s

    def update_rotation(self, dx, dy):
        dx = dx * self.sensitivity / 100000
        dy = dy * self.sensitivity / 100000
        self.rot[0] += dy
        self.rot[1] += dx
