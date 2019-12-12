from PyQt5.QtWidgets import QApplication
import os
import sys
import applogic
import figures

if __name__ == '__main__':
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    w, h = 1280, 720
    caption = '🧊Geometry SandBox'
    objects = {'Cube': figures.Cube, 'Plane': figures.Plane,
               'Ball': figures.Ball, 'Cone': figures.Cone,
               'Pyramid': figures.Pyramid, 'Tetrahedron': figures.Tetrahedron,
               'Cylinder': figures.Cylinder}

    app = QApplication(sys.argv)
    window = applogic.Application(caption, w, h, objects, 20)
    sys.exit(app.exec_())
