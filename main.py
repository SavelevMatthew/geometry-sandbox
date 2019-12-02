from PyQt5.QtWidgets import QApplication
import os
import sys
import applogic
import figures

if __name__ == '__main__':
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    w, h = 1280, 720
    caption = '🧊Geometry SandBox'
    objects = {'Cube': figures.Cube}

    app = QApplication(sys.argv)
    window = applogic.Application(caption, w, h, objects)
    sys.exit(app.exec_())
