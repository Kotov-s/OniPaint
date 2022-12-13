import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import command as cm
import io

com = cm.command()

COLORS = [
'#faffff','#c1d7db','#262245','#130e26','#34ddda','#2c9cd5',
'#213fbe','#e33d98','#9822a8','#e53a4a','#8f1157','#ffe570','#f9a135',
'#65ef42','#a8c4af','#698e86','#325555','#162527','#e3b175','#b6683c','#8a3e1b','#f5a59f'
]

class QPaletteButton(QtWidgets.QPushButton):
    def __init__(self, color):
        super().__init__()
        self.setFixedSize(QtCore.QSize(24,24))
        self.color = color
        self.setStyleSheet("background-color: %s;" % color)


class Canvas(QtWidgets.QLabel):

    def __init__(self):
        self.first_x = 0
        self.first_y = 0
        self.second_x = 0
        self.second_y = 0
        self.fig = 'rect'
        self.col = '#000000'
        super().__init__()
        
        pixmap = QtGui.QPixmap(640, 480)
        self.setPixmap(pixmap)
        self.last_x, self.last_y = None, None
        self.pen_color = QtGui.QColor(self.col)
        self.pix = QPixmap(self.rect().size())
        self.pix.fill(Qt.white)
        self.begin, self.destination = QPoint(), QPoint()	
        
    def set_pen_color(self, c):
        self.col = c
        self.pen_color = QtGui.QColor(c)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(QPoint(), self.pix)
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(self.pen_color))
        painter.setPen(pen)
        if not self.begin.isNull() and not self.destination.isNull():
            rect = QRect(self.begin, self.destination)
            if (self.fig=='rect'):
                painter.drawRect(rect.normalized())
            elif(self.fig=='ellipse'):
                painter.drawEllipse(rect.normalized())
            elif(self.fig=='line'):
                painter.drawLine(self.begin, self.destination)

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.first_x = event.x()
            self.first_y = event.y()
            self.begin = event.pos()
            self.destination = self.begin
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:		
            self.destination = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self.second_x = event.x()
        self.second_y = event.y()
        if event.button() & Qt.LeftButton:
            rect = QRect(self.begin, self.destination)
            painter = QPainter(self.pix)
            pen = QtGui.QPen()
            pen.setColor(QtGui.QColor(self.pen_color))
            painter.setPen(pen)
            brush = QtGui.QBrush()
            brush.setColor(QtGui.QColor(self.pen_color))
            brush.setStyle(Qt.SolidPattern)
            painter.setBrush(brush)
            if (self.fig=='rect'):
                painter.drawRect(rect.normalized())
                com.execute(["rect", self.first_x, self.first_y, self.second_x-self.first_x+1, self.second_y-self.first_y+1, self.col])
            elif(self.fig=='ellipse'):
                painter.drawEllipse(rect.normalized())
                com.execute(["ellipse", self.first_x, self.first_y, self.second_x-self.first_x+1, self.second_y-self.first_y+1, self.col])
            elif(self.fig=='line'):
                painter.drawLine(self.begin, self.destination)
                com.execute(["line", self.first_x, self.first_y, self.second_x, self.second_y, self.col])
            self.begin, self.destination = QPoint(), QPoint()
            self.update()
    

    def undo(self):
        com.undo()
        self.redraw()

    def redraw(self):
        painter = QtGui.QPainter(self.pix)
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor('white'))
        painter.setPen(pen)
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor('white'))
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)
        painter.drawRect(0, 0, 800, 600)
        self.update()
        painter.end()
        if (com.show_history() != -1):
            for i in range(0, len(com.show_history())):
                if (com.show_history()[i][0] == 'rect' or com.show_history()[i][0] == 'ellipse' or com.show_history()[i][0] == 'line'):
                    x = com.show_history()[i][1]
                    y = com.show_history()[i][2]
                    w = com.show_history()[i][3]
                    h = com.show_history()[i][4]
                    c = com.show_history()[i][5]
                    painter = QtGui.QPainter(self.pix)
                    pen = QtGui.QPen()
                    pen.setColor(QtGui.QColor(c))
                    painter.setPen(pen)
                    brush = QtGui.QBrush()
                    brush.setColor(QtGui.QColor(c))
                    brush.setStyle(Qt.SolidPattern)
                    painter.setBrush(brush)
                    if (com.show_history()[i][0] == 'rect'):
                        painter.drawRect(x, y, w, h)
                    elif(com.show_history()[i][0] == 'ellipse'):
                        painter.drawEllipse(x, y, w, h)
                    elif(com.show_history()[i][0] == 'line'):
                        painter.drawLine(x, y, w, h)
                    self.update()
                    painter.end()  

    def delete_all(self):
        painter = QtGui.QPainter(self.pix)
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor('white'))
        painter.setPen(pen)
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor('white'))
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)
        painter.drawRect(0, 0, 600, 600)
        com.execute(["rect", 0, 0, 600, 600, '#ffffff'])
        self.update()
        painter.end()  

    def redo(self):
        com.redo()
        self.redraw()

    def move_to_back(self):
        com.last_is_first()
        self.redraw()

    def move_to_front(self):
        com.first_is_last()
        self.redraw()

    def change_to_rect(self):
        self.fig = 'rect'

    def change_to_ellipse(self):
        self.fig = 'ellipse'

    def change_to_line(self):
        self.fig = 'line'
        
    def take_last_elem(self):
        return com.last_one()

    def move_left(self):
        temp = self.take_last_elem()
        if temp != -1:
            temp[1] -= 5
            com.delete_last(temp)
            self.redraw()

    def move_right(self):
        temp = self.take_last_elem()
        if temp != -1:
            temp[1] += 5
            com.delete_last(temp)               
            self.redraw() 

    def move_up(self):
        temp = self.take_last_elem()
        if temp != -1:
            temp[2] -= 5
            com.delete_last(temp)
            self.redraw() 

    def move_down(self):
        temp = self.take_last_elem()
        if temp != -1:
            temp[2] += 5
            com.delete_last(temp)
            self.redraw()

    def make_it_bigger(self):
        temp = self.take_last_elem()
        if temp != -1:
            temp[3] += 2
            temp[4] += 2
            com.delete_last(temp)
            self.redraw()

    def make_it_smaller(self):
        temp = self.take_last_elem()
        if temp != -1:
            temp[3] -= 2
            temp[4] -= 2
            com.delete_last(temp)
            self.redraw() 
    
    def sh_history(self):
        print(com.show_history())
        self.redraw() 

    def new_field(self):
        com.new_file()
        self.redraw()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.w = None
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setWindowTitle('OniPaint')

        self.canvas = Canvas()
        w = QtWidgets.QWidget()
        l = QtWidgets.QVBoxLayout()
        w.setLayout(l)
        l.addWidget(self.canvas)
        self.createMenuBar()
        palette = QtWidgets.QHBoxLayout()
        self.add_palette_buttons(palette)
        l.addLayout(palette)    
        buttons = QtWidgets.QHBoxLayout()
        self.add_buttons(buttons)
        l.addLayout(buttons)
        self.setCentralWidget(w)

    def show_new_window(self):
        if self.w is None:
            self.w = AnotherWindow()
        self.w.show()

    def createMenuBar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        save = QMenu("Файл", self)

        menuBar.addMenu(save)
        save.addAction('💾 Сохранить', self.save_file).setShortcut("Ctrl+S")
        save.addAction('↩️ Отменить', self.canvas.undo).setShortcut("Ctrl+Z")
        save.addAction('↪️ Вернуть', self.canvas.redo).setShortcut("Ctrl+Y")
        save.addAction('+ Новый файл', self.canvas.new_field).setShortcut("Ctrl+Shift+N")
        save.addAction('❓ Помощь', self.show_new_window).setShortcut("F1")

    def add_palette_buttons(self, layout):
        for c in COLORS:
            b = QPaletteButton(c)
            b.pressed.connect(lambda c=c: self.canvas.set_pen_color(c))
            layout.addWidget(b)

    def add_buttons(self, layout):

        fig_b = QPushButton('🗑', self)
        fig_b.pressed.connect(self.canvas.delete_all)
        layout.addWidget(fig_b)
        rect_b = QPushButton('🟨', self)
        rect_b.pressed.connect(self.canvas.change_to_rect)
        layout.addWidget(rect_b)
        circle_b = QPushButton('🟡', self)
        circle_b.pressed.connect(self.canvas.change_to_ellipse)
        layout.addWidget(circle_b)
        line_b = QPushButton('🖋', self)
        line_b.pressed.connect(self.canvas.change_to_line)
        layout.addWidget(line_b)
        first_b = QPushButton('⬆️', self)
        first_b.pressed.connect(self.canvas.move_to_front)
        layout.addWidget(first_b)   
        last_b = QPushButton('⬇️', self)
        last_b.pressed.connect(self.canvas.move_to_back)
        layout.addWidget(last_b)

        self.quitSc = QShortcut(QtCore.Qt.Key_Up, self)
        self.quitSc.activated.connect(self.canvas.move_up)
        self.quitSc = QShortcut(QtCore.Qt.Key_Down, self)
        self.quitSc.activated.connect(self.canvas.move_down)
        self.quitSc = QShortcut(QtCore.Qt.Key_Right, self)
        self.quitSc.activated.connect(self.canvas.move_right)               
        self.quitSc = QShortcut(QtCore.Qt.Key_Left, self)
        self.quitSc.activated.connect(self.canvas.move_left)
        self.quitSc = QShortcut("Ctrl+P", self)
        self.quitSc.activated.connect(self.canvas.make_it_bigger)
        self.quitSc = QShortcut("Ctrl+M", self)
        self.quitSc.activated.connect(self.canvas.make_it_smaller)   
        self.quitSc = QShortcut("Ctrl+H", self)
        self.quitSc.activated.connect(self.canvas.sh_history)           
    
    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "PNG Image file (*.png)")
        if path:
            pixmap = self.canvas.pix
            pixmap.save(path, "PNG" )

class AnotherWindow(QWidget):
    def __init__(self):
        super().__init__()
        f = io.open("help.txt", mode="r", encoding="utf-8")
        self.setWindowIcon(QtGui.QIcon('help.png'))
        self.setWindowTitle("Помощь")
        self.layout = QVBoxLayout()
        message = QLabel(str(f.read()))
        self.layout.addWidget(message)
        self.setLayout(self.layout)

app = QtWidgets.QApplication(sys.argv)
app.setWindowIcon(QIcon('icon.png'))
window = MainWindow()
window.show()
app.exec_()   