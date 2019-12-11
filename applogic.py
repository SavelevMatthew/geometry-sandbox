from PyQt5.QtWidgets import (QMainWindow, QWidget, QListWidget, QLabel,
                             QPushButton, QListWidgetItem, QFrame, QGridLayout,
                             QInputDialog, QMessageBox, QAbstractItemView,
                             QAction, QMenuBar)
from PyQt5.QtCore import Qt, QBasicTimer
from PyQt5.QtGui import QPainter, QPen, QFont
import figures
from engine import Engine
from math import pi
from camera import Cam
from numpy import vstack, hstack, ones, cross


class Application(QMainWindow):
    def __init__(self, caption, w, h, available_objects, precision):
        super().__init__()
        self.caption = caption
        self.w = w
        self.h = h
        self.keyboard = {'A': False, 'D': False, 'W': False, 'S': False,
                         'SHIFT': False, 'SPACE': False}
        self.avaliable = available_objects
        self.precision = precision

        self.setFixedSize(w, h)
        self.setWindowTitle(caption)

        self.cam = Cam((0, 50, 0))
        self.engine = Engine(self.cam)
        self.pointer = Pointer()

        self.canvas = Canvas(self, w * 0.75, h, 0, 0, 'rgba(100,100,100,100%)',
                             self.engine)
        self.selector = ObjectSelector(w / 4, h / 3, 'Select figure to Create',
                                       self, 'rgba(50,50,50,100%)',
                                       self.avaliable)
        self.move_window = MoveWindow(self, w / 3, h / 3, 'Move object',
                                      -10000, 10000, 2, 0.0)
        self.scale_window = ScaleWindow(self, w / 3, h / 3, 'Scale object',
                                        0.01, 10, 2, 1.0)
        self.rotate_window = RotateWindow(self, w / 3, h / 3, 'Rotate object',
                                          0, 360, 2, 0.0)
        self.objects = SideBar(self, w * 0.25, h, w * 0.75, 0,
                               'rgba(50,50,50,100%)')

        main_menu = self.menuBar()
        camera_menu = main_menu.addMenu('Camera')

        reset_camera = QAction('Reset', camera_menu)
        reset_camera.setStatusTip('Reset camera position and mode')
        reset_camera.triggered.connect(self.reset_camera)
        self.switch_camera = QAction('Mode: Free flight', camera_menu)
        self.switch_camera.setStatusTip('Switching camera mode...')
        self.switch_camera.triggered.connect(self.switch_camera_mode)

        camera_menu.addAction(self.switch_camera)
        camera_menu.addAction(reset_camera)

        self.timer = QBasicTimer()
        self.frames = 60
        self.dt = int(100 / self.frames)
        self.timer.start(self.dt, self)
        self.show()

    def keyPressEvent(self, event):
        key = event.key()
        if self.canvas.hasFocus():
            if key == Qt.Key_A:
                self.keyboard['A'] = True
            elif key == Qt.Key_D:
                self.keyboard['D'] = True
            elif key == Qt.Key_W:
                self.keyboard['W'] = True
            elif key == Qt.Key_S:
                self.keyboard['S'] = True
            elif key == Qt.Key_Space:
                self.keyboard['SPACE'] = True
            elif key == Qt.Key_Shift:
                self.keyboard['SHIFT'] = True

    def keyReleaseEvent(self, event):
        key = event.key()
        if key == Qt.Key_A:
            self.keyboard['A'] = False
        elif key == Qt.Key_D:
            self.keyboard['D'] = False
        elif key == Qt.Key_W:
            self.keyboard['W'] = False
        elif key == Qt.Key_S:
            self.keyboard['S'] = False
        elif key == Qt.Key_Space:
            self.keyboard['SPACE'] = False
        elif key == Qt.Key_Shift:
            self.keyboard['SHIFT'] = False

    def timerEvent(self, event):
        dx, dy = self.pointer.get_movement()
        self.cam.update_rotation(dx, dy)
        self.cam.update_position(self.dt, self.keyboard)
        self.canvas.repaint()

    def add_object(self, obj):
        self.engine.add_object(obj)
        list_object = ListObject(obj.name, self.objects.list)
        self.objects.list.addItem(list_object)
        self.objects.list.clearSelection()
        self.objects.list.setCurrentItem(list_object)

    def delete_object(self, name):
        items = self.objects.list.findItems(name, Qt.MatchExactly)
        if len(items) > 0:
            row = self.objects.list.row(items[0])
            self.objects.list.takeItem(row)
        self.engine.delete_item(name)

    def switch_camera_mode(self):
        if self.cam.mode == 0:
            self.cam.mode = 1
            self.switch_camera.setText('Mode: Centered')
        else:
            self.cam.mode = 0
            self.switch_camera.setText('Mode: Free Flight')
        self.reset_camera()

    def reset_camera(self):
        self.cam.pos = [0, 50, 0]
        self.cam.rot = [0, 0, 0]


class Canvas(QWidget):
    def __init__(self, parent, w, h, offset_x, offset_y, bg, engine):
        super().__init__()
        self.w = w
        self.h = h
        self.engine = engine
        self.parent = parent
        self.cam = engine.cam
        self.cx, self.cy = w // 2, h // 2
        self.pos = (offset_x, offset_y)
        self.mouse_pressed = False
        self.lines = [((0, 0), (0, w)), ((0, w), (w, h)),
                      ((w, h), (0, h)), ((0, h), (0, 0))]
        self.axises = figures.Axises()

        self.setFixedSize(w, h)
        self.setParent(parent)
        self.setStyleSheet('background-color: {}'.format(bg))
        self.move(offset_x, offset_y)
        self.setMouseTracking(True)
        self.show()

        self.border_brush = QPen(Qt.black, int(w / 200), Qt.SolidLine)
        self.verts_brush = QPen(Qt.black, int(w / 70), Qt.SolidLine)

    def mousePressEvent(self, event):
        self.setFocus()
        self.parent.selector.hide()
        self.parent.move_window.hide()
        self.parent.scale_window.hide()
        self.parent.rotate_window.hide()
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = True
            self.parent.pointer.click(event.x(), event.y())

    def mouseReleaseEvent(self, event):
        self.mouse_pressed = False

    def mouseMoveEvent(self, event):
        if self.mouse_pressed:
            self.parent.pointer.update_position(event.x(), event.y())

    def paintEvent(self, event):
        self.painter = QPainter(self)
        self.draw_axis(self.w / 10)

        for i in self.engine.figures:
            figure = self.engine.figures[i]
            self.draw_figure(figure)
        self.painter.end()
        # pygame.draw.line(screen, clrs.black, points[0], points[1], 1)

    def draw_figure(self, figure):
        for edge in figure.edges:
            points = []
            for x, y, z in (figure.vertices[edge[0]],
                            figure.vertices[edge[1]]):
                if self.cam.mode == 0:
                    x -= self.cam.pos[0]
                    y -= self.cam.pos[1]
                    z -= self.cam.pos[2]

                    x, y = Engine.rotate2d((x, y), -self.cam.rot[1])
                    z, y = Engine.rotate2d((z, y), self.cam.rot[0])
                else:
                    x, y, z = Engine.rotate_vert((x, y, z), self.cam.rot[0], 0,
                                                 self.cam.rot[1])
                    x -= self.cam.pos[0]
                    y -= self.cam.pos[1]
                    z -= self.cam.pos[2]

                if y > -0.01:
                    y = 0.01
                f = -300 / abs(y)
                x, y = x * f, z * f
                points += [(self.cx - x, self.cy + y)]
                self.painter.setPen(self.verts_brush)
                if self.is_point_inside((self.cx - x, self.cy + y)):
                    self.painter.drawPoint(self.cx - x, self.cy + y)

            self.painter.setPen(self.border_brush)
            self.painter.drawLine(points[0][0], points[0][1],
                                  points[1][0], points[1][1])

    def is_point_inside(self, p):
        return p[0] >= 0 and p[0] < self.w and p[1] >= 0 and p[1] < self.h


class SideBar(QWidget):
    def __init__(self, parent, w, h, offset_x, offset_y, bg):
        super().__init__()
        self.w = w
        self.h = h
        self.pos = (offset_x, offset_y)
        self.parent = parent

        self.setFixedSize(w, h)
        self.setParent(parent)
        self.move(offset_x, offset_y)
        self.show()

        self.bg = QLabel()
        self.bg.setFixedSize(w, h)
        self.bg.setParent(self)
        self.bg.setStyleSheet('background-color: {}'.format(bg))
        self.bg.show()
        list_h = h - w / 5
        self.list = ObjList(self, w, list_h, 0, 0, 'rgba(75,75,75,100%)')

        btn_bg = 'rgba(200,200,200,100%)'
        style = 'background-color: {0}; border-color: {3}; \
                 border-style: solid; \
                 border-width: {1}px {2}px 0px 0px'.format(btn_bg,
                                                           int(w * 0.02),
                                                           int(w * 0.01), bg)
        self.add = QPushButton(' ➕', self)
        self.add.setFixedSize(w / 5, w / 5)
        self.add.move(0, list_h)
        self.add.setStyleSheet(style)
        self.add.setFont(QFont('Arial', int(w / 12), QFont.Bold))
        self.add.clicked.connect(self.parent.selector.show)
        self.add.clicked.connect(self.parent.scale_window.hide)
        self.add.clicked.connect(self.parent.move_window.hide)
        self.add.clicked.connect(self.parent.rotate_window.hide)
        self.add.show()

        style = 'background-color: {0}; border-color: {3}; \
                 border-style: solid; \
                 border-width: {1}px {2}px 0px'.format(btn_bg,
                                                       int(w * 0.02),
                                                       int(w * 0.01), bg)
        self.bin = QPushButton(' 🗑', self)
        self.bin.setFixedSize(w / 5, w / 5)
        self.bin.move(w * 0.2, list_h)
        self.bin.setStyleSheet(style)
        self.bin.setFont(QFont('Arial', int(w / 12), QFont.Bold))
        self.bin.clicked.connect(self.parent.selector.hide)
        self.bin.clicked.connect(self.parent.scale_window.hide)
        self.bin.clicked.connect(self.parent.move_window.hide)
        self.bin.clicked.connect(self.parent.rotate_window.hide)
        self.bin.clicked.connect(self.delete_object)
        self.bin.show()

        self.mv = QPushButton(' ⇵ ', self)
        self.mv.setFixedSize(w / 5, w / 5)
        self.mv.move(w * 0.4, list_h)
        self.mv.setStyleSheet(style)
        self.mv.setFont(QFont('Arial', int(w / 12), QFont.Bold))
        self.mv.clicked.connect(self.parent.move_window.show)
        self.mv.clicked.connect(self.parent.rotate_window.hide)
        self.mv.clicked.connect(self.parent.scale_window.hide)
        self.mv.clicked.connect(self.parent.selector.hide)
        self.mv.clicked.connect(self.check_for_objects)
        self.mv.show()

        self.rot = QPushButton(' ⟲ ', self)
        self.rot.setFixedSize(w / 5, w / 5)
        self.rot.move(w * 0.6, list_h)
        self.rot.setStyleSheet(style)
        self.rot.setFont(QFont('Arial', int(w / 6), QFont.Bold))
        self.rot.clicked.connect(self.parent.rotate_window.show)
        self.rot.clicked.connect(self.parent.scale_window.hide)
        self.rot.clicked.connect(self.parent.move_window.hide)
        self.rot.clicked.connect(self.parent.selector.hide)
        self.rot.clicked.connect(self.check_for_objects)
        self.rot.show()

        style = 'background-color: {0}; border-color: {3}; \
                 border-style: solid; \
                 border-width: {1}px 0px 0px {2}px'.format(btn_bg,
                                                           int(w * 0.02),
                                                           int(w * 0.01), bg)
        self.sc = QPushButton('⇱⇲', self)
        self.sc.setFixedSize(w / 5, w / 5)
        self.sc.move(w * 0.8, list_h)
        self.sc.setStyleSheet(style)
        self.sc.setFont(QFont('Arial', int(w / 10), QFont.Bold))
        self.sc.clicked.connect(self.parent.scale_window.show)
        self.sc.clicked.connect(self.parent.move_window.hide)
        self.sc.clicked.connect(self.parent.rotate_window.hide)
        self.sc.clicked.connect(self.parent.selector.hide)
        self.sc.clicked.connect(self.check_for_objects)
        self.sc.show()

    def check_for_objects(self):
        if len(self.parent.objects.list.selectedItems()) == 0:
            self.parent.scale_window.hide()
            self.parent.move_window.hide()
            self.parent.rotate_window.hide()

    def delete_object(self):
        items = self.parent.objects.list.selectedItems()
        if len(items) == 0:
            return
        names = ''
        for item in items:
            names += item.text() + ', '
        names = names[:-2:]
        formatted_msg = 'Are you sure about deleting {}?'.format(names)
        msg = QMessageBox()
        msg.setWindowTitle('Deleting object!')
        msg.setText('You\'re trying to delete object.' +
                    ' This operation can\'t be cancelled!')
        msg.setInformativeText(formatted_msg)
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        res = msg.exec_()
        if res == QMessageBox.Ok:
            for item in items:
                self.parent.delete_object(item.text())


class ObjList(QListWidget):
    def __init__(self, parent, w, h, offset_x, offset_y, bg):
        super().__init__()
        self.w = w
        self.h = h
        self.pos = (offset_x, offset_y)
        self.app = parent.parent

        self.setFixedSize(w, h)
        self.setParent(parent)
        self.move(offset_x, offset_y)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.show()

        self.itemDoubleClicked.connect(self.rename_item)

    def rename_item(self, item):
        formatted_msg = 'Enter new name for {}:'.format(item.text())
        text, ok = QInputDialog.getText(self, 'Renaming object', formatted_msg)
        if ok:
            text = str(text)
            if len(text) == 0:
                return
            items = self.app.objects.list.findItems(text, Qt.MatchExactly)
            if text != item.text() and len(items) > 0:
                msg = QMessageBox()
                msg.setWindowTitle('Renaming object')
                msg.setText('Renamimg object is imposssible!')
                formatted_msg = 'Object with name {}'.format(text) + \
                                ' already exists...'
                msg.setInformativeText(formatted_msg)
                msg.setIcon(QMessageBox.Warning)
                msg.setStandardButtons(QMessageBox.Ok)
                res = msg.exec_()
                return
            if text != item.text():
                old_name = item.text()
                object = self.app.engine.figures[old_name]
                self.app.delete_object(old_name)
                object.name = text
                self.app.add_object(object)


class ListObject(QListWidgetItem):
    def __init__(self, name, parent):
        super().__init__(parent)
        self.name = name

        self.setText(name)
        self.setTextAlignment(Qt.AlignCenter)


class ObjectSelector(QWidget):
    def __init__(self, w, h, caption, app, bg, objects):
        super().__init__()
        self.caption = caption
        self.w = w
        self.h = h
        self.bg = bg
        self.objects = objects
        self.app = app

        self.setWindowTitle(caption)
        self.setFixedSize(w, h)
        self.hide()

        self.bg = QLabel()
        self.bg.setFixedSize(w, h)
        self.bg.setParent(self)
        self.bg.setStyleSheet('background-color: {}'.format(bg))
        self.bg.show()

        self.list = QListWidget()
        self.list.setParent(self)
        self.list.setFixedSize(w * 0.75, h * 0.75)
        self.list.move(w * 0.125, 0)
        self.list.show()

        for i in self.objects:
            self.list.addItem(ListObject(i, self.list))
        self.list.setCurrentRow(0)

        self.add = QPushButton('Add', self)
        self.add.setFixedSize(w * 0.5, h * 0.25)
        self.add.move(w * 0.25, h * 0.75)
        self.add.clicked.connect(self.add_object)
        self.add.clicked.connect(self.hide)
        self.add.show()

    def add_object(self):
        name = self.list.currentItem().text()
        if self.objects[name].precise_depend:
            precision, ok = QInputDialog.getInt(self, 'Input precision',
                                                'Enter value: ', 4, 3,
                                                self.app.precision, 1)
            if ok:
                figure_name = self.app.engine.generate_name(name)
                figure = self.objects[name](figure_name, precision)
                self.app.add_object(figure)
        else:
            figure_name = self.app.engine.generate_name(name)
            figure = self.objects[name](figure_name)
            self.app.add_object(figure)


class ModifyWindow(QWidget):
    def __init__(self, app, w, h, caption, min, max, uncertainty, default):
        super().__init__()
        self.w = w
        self.h = h
        self.cap = caption
        self.x = default
        self.y = default
        self.z = default
        self.default = default
        self.min = min
        self.max = max
        self.uncertainty = uncertainty
        self.app = app

        self.setFixedSize(w, h)
        self.setWindowTitle(caption)

        label1 = QLabel('X: ')
        label2 = QLabel('Y: ')
        label3 = QLabel('Z: ')
        self.x_label = QLabel(str(default))
        self.x_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.y_label = QLabel(str(default))
        self.y_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.z_label = QLabel(str(default))
        self.z_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.x_button = QPushButton('Change')
        self.x_button.clicked.connect(self.set_x)
        self.y_button = QPushButton('Change')
        self.y_button.clicked.connect(self.set_y)
        self.z_button = QPushButton('Change')
        self.z_button.clicked.connect(self.set_z)
        self.ok_button = QPushButton('OK')

        main_layout = QGridLayout()
        main_layout.addWidget(QLabel(), 0, 0, 1, 6)
        main_layout.addWidget(label1, 1, 0)
        main_layout.addWidget(self.x_label, 1, 1)
        main_layout.addWidget(label2, 1, 2)
        main_layout.addWidget(self.y_label, 1, 3)
        main_layout.addWidget(label3, 1, 4)
        main_layout.addWidget(self.z_label, 1, 5)
        main_layout.addWidget(self.x_button, 2, 0, 1, 2)
        main_layout.addWidget(self.y_button, 2, 2, 1, 2)
        main_layout.addWidget(self.z_button, 2, 4, 1, 2)
        main_layout.addWidget(self.ok_button, 3, 2, 2, 2)
        main_layout.setColumnMinimumWidth(1, w / 4)
        main_layout.setColumnMinimumWidth(3, w / 4)
        main_layout.setColumnMinimumWidth(5, w / 4)
        self.setLayout(main_layout)

    def set_x(self):
        double, ok = QInputDialog.getDouble(self, 'Change value',
                                            'Enter new value: ', self.default,
                                            self.min, self.max,
                                            self.uncertainty)
        if ok:
            self.x_label.setText('{}'.format(double))
            self.x = double

    def set_y(self):
        double, ok = QInputDialog.getDouble(self, 'Change value',
                                            'Enter new value: ', self.y,
                                            self.min, self.max,
                                            self.uncertainty)
        if ok:
            self.y_label.setText('{}'.format(double))
            self.y = double

    def set_z(self):
        double, ok = QInputDialog.getDouble(self, 'Change value',
                                            'Enter new value: ', self.z,
                                            self.min, self.max,
                                            self.uncertainty)
        if ok:
            self.z_label.setText('{}'.format(double))
            self.z = double

    def clear_values(self):
        self.x = self.default
        self.y = self.default
        self.z = self.default
        self.x_label.setText(str(self.x))
        self.y_label.setText(str(self.y))
        self.z_label.setText(str(self.z))


class MoveWindow(ModifyWindow):
    def __init__(self, *args):
        super().__init__(*args)
        self.ok_button.clicked.connect(self.move_object)

    def move_object(self):
        items = self.app.objects.list.selectedItems()
        for item in items:
            name = item.text()
            self.app.engine.figures[name].move(self.x, self.y, self.z)
        self.clear_values()
        self.hide()


class ScaleWindow(ModifyWindow):
    def __init__(self, *args):
        super().__init__(*args)
        self.ok_button.clicked.connect(self.scacle_object)

    def scacle_object(self):
        items = self.app.objects.list.selectedItems()
        for item in items:
            name = item.text()
            self.app.engine.figures[name].scale(self.x, self.y, self.z)
        self.clear_values()
        self.hide()


class RotateWindow(ModifyWindow):
    def __init__(self, *args):
        super().__init__(*args)
        self.ok_button.clicked.connect(self.rotate_object)

    def rotate_object(self):
        items = self.app.objects.list.selectedItems()
        for item in items:
            name = item.text()
            self.app.engine.figures[name].rotate(self.x, self.y, self.z)
        self.clear_values()
        self.hide()


class Pointer():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.x_onclick = 0
        self.y_onclick = 0

    def get_movement(self):
        dx = self.x - self.x_onclick
        dy = self.y - self.y_onclick
        self.x_onclick = self.x
        self.y_onclick = self.y
        return dx, dy

    def click(self, x, y):
        self.x = self.x_onclick = x
        self.y = self.y_onclick = y

    def update_position(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
