import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import command as cm
import numpy as np
import cv2
from PIL import Image
import markdown

com = cm.command()

class Canvas(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.first_x = 0
        self.first_y = 0
        self.second_x = 0
        self.second_y = 0
        self.fig = 'brush'
        self.fill = False
        self.brush_history = []
        self.image_path = ''
        self.col = QColor(0, 0, 0)
        pixmap = QtGui.QPixmap(640, 480)
        self.setPixmap(pixmap)
        self.last_x, self.last_y = None, None
        self.pix = QPixmap(self.rect().size())
        self.pix.fill(Qt.white)
        self.begin, self.destination = QPoint(), QPoint()
        self.brush_size = 1	

    def set_brush_size(self, s):
        self.brush_size = s

    def set_pen_color(self, c):
        self.col = c
        self.pen_color = QtGui.QColor(c)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(QPoint(), self.pix)
        painter.translate(QPoint(0, 0))
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(self.col))
        painter.setPen(pen)
        if not self.begin.isNull() and not self.destination.isNull():
            rect = QRect(self.begin, self.destination)
            if (self.fig=='rect'):
                painter.drawRect(rect.normalized())
            elif(self.fig=='ellipse'):
                painter.drawEllipse(rect.normalized())
            elif(self.fig=='line'):
                painter.drawLine(self.begin, self.destination)
            elif(self.fig=='brush'):
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
            if self.fig == 'brush':
                painter = QPainter(self.pix)
                painter.setRenderHint(QPainter.Antialiasing, True)
                pen = QtGui.QPen(QtGui.QColor(self.col), self.brush_size)
                painter.setPen(pen)
                brush = QtGui.QBrush()
                brush.setColor(QtGui.QColor(self.col))
                brush.setStyle(Qt.SolidPattern)
                self.begin = event.pos()
                self.brush_history.append(self.first_x)
                self.brush_history.append(self.first_y)
                self.first_x = event.x()
                self.first_y = event.y()
                painter.drawLine(self.begin, self.destination)
                self.brush_history.append(self.first_x)
                self.brush_history.append(self.first_y)
                self.destination = self.begin
                self.update()
            else:	
                self.destination = event.pos()
                self.update()

    def mouseReleaseEvent(self, event):
        self.second_x = event.x()
        self.second_y = event.y()
        if event.button() & Qt.LeftButton:
            rect = QRect(self.begin, self.destination)
            painter = QPainter(self.pix)
            painter.setRenderHint(QPainter.Antialiasing, True)
            pen = QtGui.QPen(QtGui.QColor(self.col), self.brush_size)
            painter.setPen(pen)
            brush = QtGui.QBrush()
            brush.setColor(QtGui.QColor(self.col))
            if (self.fill):
                brush.setStyle(Qt.SolidPattern)
            painter.setBrush(brush)
            if (self.fig=='rect'):
                painter.drawRect(rect.normalized())
                com.execute(["rect", self.first_x, self.first_y, self.second_x-self.first_x+1, self.second_y-self.first_y+1, self.col, self.brush_size, self.fill])
            elif(self.fig=='ellipse'):
                painter.drawEllipse(rect.normalized())
                com.execute(["ellipse", self.first_x, self.first_y, self.second_x-self.first_x+1, self.second_y-self.first_y+1, self.col, self.brush_size, self.fill])
            elif(self.fig=='line'):
                painter.drawLine(self.begin, self.destination)
                com.execute(["line", self.first_x, self.first_y, self.second_x, self.second_y, self.col, self.brush_size])
            elif(self.fig=='brush'):
                painter.drawLine(self.begin, self.destination)
                if (self.brush_history != []):
                    com.execute(["brush", self.brush_history, self.col, self.brush_size])
                self.brush_history = []
            self.begin, self.destination = QPoint(), QPoint()
            self.update()
    
    def undo(self):
        com.undo()
        self.redraw()

    def redraw(self):
        painter = QtGui.QPainter(self.pix) 
        painter.setRenderHint(QPainter.Antialiasing, True)
        if (self.image_path == ''):         
            self.pix.fill(Qt.white)
        else:
            self.pix.fill(Qt.transparent)
            image = QPixmap(self.image_path)
            painter.drawPixmap(0, 0, image) 
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor('white'))
        painter.setPen(pen)
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor('white'))
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)
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
                    s = com.show_history()[i][6]
                    painter = QtGui.QPainter(self.pix)
                    painter.setRenderHint(QPainter.Antialiasing, True)  
                    pen = QtGui.QPen(QtGui.QColor(c), s)   
                    painter.setPen(pen)
                    brush = QtGui.QBrush()
                    brush.setColor(QtGui.QColor(c)) 
                    if (com.show_history()[i][0] == 'rect' or com.show_history()[i][0] == 'ellipse'):
                        if (com.show_history()[i][7]):
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
                elif com.show_history()[i][0] == 'brush':
                    l = com.show_history()[i][1]
                    c = com.show_history()[i][2]
                    s = com.show_history()[i][3]
                    painter = QtGui.QPainter(self.pix)
                    painter.setRenderHint(QPainter.Antialiasing, True)
                    pen = QtGui.QPen(QtGui.QColor(c), s) 
                    painter.setPen(pen)
                    brush = QtGui.QBrush()
                    brush.setColor(QtGui.QColor(c))
                    brush.setStyle(Qt.SolidPattern)
                    painter.setBrush(brush)
                    for i in range(0, len(l)-3,  4):
                        painter.drawLine(l[i], l[i+1], l[i+2], l[i+3])
                    self.update()
                    painter.end()
                elif com.show_history()[i][0] == 'text':  
                    x = com.show_history()[i][1]
                    y = com.show_history()[i][2]
                    text = com.show_history()[i][3]
                    c = com.show_history()[i][4]
                    family = com.show_history()[i][5]
                    size = com.show_history()[i][6]
                    painter = QtGui.QPainter(self.pix)
                    pen = QtGui.QPen(QtGui.QColor(c)) 
                    painter.setPen(pen)
                    font = QtGui.QFont(family, size)
                    painter.setFont(font)
                    painter.drawText(x, y, text)
                    self.update()
                    painter.end()                

    def redo(self):
        com.redo()
        self.redraw()

    def change_tool(self, tool):
        self.fig = tool
    
    def add_text(self, text, font_size, font_family):
        if text:
            painter = QPainter(self.pix)
            pen = QtGui.QPen()
            pen.setColor(QtGui.QColor(self.col))
            painter.setPen(pen)
            font = QtGui.QFont(font_family, font_size)
            painter.setFont(font)
            painter.drawText(self.first_x, self.first_y, text)
            com.execute(["text", self.first_x, self.first_y, text, self.col, font_family, font_size])
            self.update()

    def converting_to_bw(self):
        self.pix = self.pix.toImage().convertToFormat(QImage.Format_Grayscale8)
        self.pix = QPixmap.fromImage(self.pix)
        self.update()

    def inversing(self):
        img = self.to_arr()
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        inv = cv2.bitwise_not(img_bgr)
        self.changed_image(inv)

    def blurring(self):
        img = self.to_arr()
        blurred = cv2.blur(img, (25, 25))
        self.changed_image(blurred)

    def data_moshing(self):
        img = self.to_arr()
        mosh_factor = 20
        blue_channel = img[:, :, 0]
        height, width = blue_channel.shape
        shuffled_indices = np.arange(height)
        np.random.shuffle(shuffled_indices)
        for i in range(height):
            row_index = shuffled_indices[i]
            blue_channel[row_index, :] = np.roll(blue_channel[row_index, :], np.random.randint(-mosh_factor, mosh_factor))
        img[:, :, 0] = blue_channel
        self.changed_image(img)

    def motion_blurring(self):
        img = self.to_arr()
        kernel_size = 20
        kernel = np.zeros((kernel_size, kernel_size))
        kernel[int((kernel_size-1)/2), :] = np.ones(kernel_size)
        kernel = kernel / kernel_size
        motion_blur = cv2.filter2D(img, -2, kernel)
        self.changed_image(motion_blur)

    def pixilization(self):
        img = self.to_arr()
        height, width = img.shape[:2]
        pixel_size = 20
        small_img = cv2.resize(img, (width // pixel_size, height // pixel_size), interpolation=cv2.INTER_NEAREST)
        pixelated = cv2.resize(small_img, (width, height), interpolation=cv2.INTER_NEAREST)
        self.changed_image(pixelated)

    def emboss(self):    
        img = self.to_arr()
        kernel = np.array([[-2, -1, 0],
                        [-1, 1, 1],
                        [0, 1, 2]])
        emboss = cv2.filter2D(img, -1, kernel)
        self.changed_image(emboss)


    def sepia(self):
        img = self.to_arr()
        bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        kernel = np.array([[0.393, 0.769, 0.189],
                        [0.349, 0.686, 0.168],
                        [0.272, 0.534, 0.131]])
        sepia = cv2.transform(bgr, kernel)
        self.changed_image(sepia)

    def cartoonization(self):
        img = self.to_arr()
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(img_bgr, 9, 300, 300)
        color = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        self.changed_image(cartoon)

    def sketch(self):    
        img = self.to_arr()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        edges = cv2.Canny(gray, 100, 200)
        edges = cv2.bitwise_not(edges)
        sketch = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        self.changed_image(sketch)

    def mirror(self):
        mirror = cv2.flip(self.to_arr(), 1)
        self.changed_image(mirror)

    def mirror_g(self):
      mirror = cv2.flip(self.to_arr(), 0)
      self.changed_image(mirror)

    def rotate(self, angle):

        try:
            if (angle == 90):
                img_cw = cv2.rotate(self.to_arr(), cv2.ROTATE_90_CLOCKWISE)
            elif (angle == 180):
                img_cw = cv2.rotate(self.to_arr(), cv2.ROTATE_180)
            elif (angle == 270):
                img_cw = cv2.rotate(self.to_arr(), cv2.ROTATE_90_COUNTERCLOCKWISE)
            self.changed_image(img_cw)
        except:
            pass


    def rotate_90(self):
      img_cw_90 = cv2.rotate(self.to_arr(), cv2.ROTATE_90_CLOCKWISE)
      self.changed_image(img_cw_90)

    def rotate_180(self):
      img_cw_180 = cv2.rotate(self.to_arr(), cv2.ROTATE_180)
      self.changed_image(img_cw_180)

    def rotate_270(self):
      img_cw_270 = cv2.rotate(self.to_arr(), cv2.ROTATE_90_COUNTERCLOCKWISE)
      self.changed_image(img_cw_270)

    def changed_image(self, image):
        h, w, c = image.shape
        if c == 3:
            qImg = QImage(image.data, w, h, w * c, QImage.Format_RGB888)
        elif c == 4:
            qImg = QImage(image.data, w, h, w * c, QImage.Format_RGBA8888)
        else:
            raise ValueError("Изображение должно иметь 3 или 4 канала")
        pixmap = QPixmap.fromImage(qImg)
        self.pix = pixmap
        self.setFixedSize(pixmap.size())
        self.update()

    def to_arr(self):
        self.scale_factor = 1
        pixmap = self.grab()
        img = pixmap.toImage()
        img = img.convertToFormat(QImage.Format_RGBA8888)
        width, height = pixmap.width(), pixmap.height()
        ptr = img.constBits()
        ptr.setsize(img.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)
        return arr
    
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.w = None
        self.setWindowTitle('PyPaint')
        self.setWindowIcon(QIcon('icons/artist.ico'))
        self.canvas = Canvas()
        self.setMinimumSize(QtCore.QSize(664,630))
        self.setGeometry(QtCore.QRect(500,100,664,630))
        w = QtWidgets.QWidget()
        l = QtWidgets.QVBoxLayout(spacing = 10)
        buttons = QtWidgets.QHBoxLayout()
        self.add_buttons(buttons)
        l.addLayout(buttons)
        palette = QtWidgets.QVBoxLayout()
        self.add_palette_buttons(palette)
        l.addLayout(palette)
        self.setCentralWidget(w) 
        w.setLayout(l)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.canvas)
        l.addWidget(scroll)
        self.createMenuBar()
        self.createEffectsMenuBar()
        self.createFlippingMenuBar()

    def show_color_picker(self):
        color = QColorDialog.getColor(self.canvas.col, self, "Выбор цвета")
        if color.isValid():
            self.canvas.col = color

    def show_help_window(self):
        if self.w is None:
            self.w = HelpWindow()
        self.w.show()

    def show_text_window(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ввод текста")
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint) 
        label1 = QLabel("Введите текст:", dialog)
        line_edit1 = QLineEdit(dialog)
        label2 = QLabel("Введите размер шрифта:", dialog)
        spin_box1 = QSpinBox(dialog)
        spin_box1.setMinimum(8)
        spin_box1.setMaximum(48)
        label4 = QLabel("Выберите семейство шрифтов:", dialog)
        combo_box = QComboBox(dialog)
        combo_box.addItem("Times New Roman")
        combo_box.addItem("Comic Sans MS")
        combo_box.addItem("Helvetica")
        combo_box.addItem("Impact")
        combo_box.addItem("Arial")
        layout = QVBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(line_edit1)
        layout.addWidget(label2)
        layout.addWidget(spin_box1)
        layout.addWidget(label4)
        layout.addWidget(combo_box)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, dialog)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog_layout = QVBoxLayout()
        dialog_layout.addLayout(layout)
        dialog_layout.addWidget(button_box, alignment=Qt.AlignBottom | Qt.AlignCenter)
        dialog.setLayout(dialog_layout)
        label1.setText("Введите текст:")
        label2.setText("Введите размер шрифта:")
        label4.setText("Выберите опцию:")
        button_box.button(QDialogButtonBox.Ok).setText("ОК")
        button_box.button(QDialogButtonBox.Cancel).setText("Отмена")

        if dialog.exec_() == QDialog.Accepted:
            text_value = line_edit1.text()
            int_value1 = spin_box1.value()
            combo_value = combo_box.currentText()
            self.canvas.add_text(text_value, int_value1, combo_value)

    def open_image(self):
        com.new_file()
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        
        if path:
            image = QImage(path)
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                self.canvas.pix = pixmap
                self.canvas.image_path = path
                self.canvas.setFixedSize(pixmap.size())
                self.canvas.update()

    def createFlippingMenuBar(self):
        menuBar = self.menuBar()
        rotate = QMenu("Поворот изображения", self)
        menuBar.addMenu(rotate)
        rotate.addAction('Отзеркаливание по горизонтали', self.canvas.mirror)
        rotate.addAction('Отзеркаливание по вертикали', self.canvas.mirror_g)
        rotate.addAction('Повернуть на 90°', lambda: self.canvas.rotate(90))
        rotate.addAction('Повернуть на 270°',lambda: self.canvas.rotate(270))
        rotate.addAction('Повернуть на 180°',lambda: self.canvas.rotate(180))

    def createEffectsMenuBar(self):
        menuBar = self.menuBar()
        effects = QMenu("Эффекты", self)
        menuBar.addMenu(effects)
        effects.addAction('Сделать черно-белым', self.canvas.converting_to_bw)
        effects.addAction('Инверсия', self.canvas.inversing)
        effects.addAction('Сепия', self.canvas.sepia)
        effects.addAction('Размытие', self.canvas.blurring)
        effects.addAction('Размытие в движении', self.canvas.motion_blurring)
        effects.addAction('Глитч', self.canvas.data_moshing)
        effects.addAction('Пикслелизация', self.canvas.pixilization)
        effects.addAction('Тиснение', self.canvas.emboss)
        effects.addAction('Карикатура', self.canvas.cartoonization)
        effects.addAction('Рисунок карандашом', self.canvas.sketch)

    def createMenuBar(self):
        menuBar = self.menuBar()
        save = QMenu("Файл", self)
        menuBar.addMenu(save)
        save.addAction('💾 Сохранить', self.save_file).setShortcut("Ctrl+S")
        save.addAction('📂 Открыть изображение', self.open_image).setShortcut("Ctrl+O")
        save.addAction('↩️ Отменить', self.canvas.undo).setShortcut("Ctrl+Z")
        save.addAction('↪️ Вернуть', self.canvas.redo).setShortcut("Ctrl+Y")
        save.addAction('❓ Помощь', self.show_help_window).setShortcut("F1")

    def add_palette_buttons(self, layout):
        slader_label = QLabel("Размер линии:", self)
        slader_label.setMaximumSize(QtCore.QSize(90, 22))
        layout.addWidget(slader_label)        
        slider = QSlider(Qt.Horizontal, self)
        slider.setMaximumSize(QtCore.QSize(170, 22))
        slider.setRange(1, 8)
        slider.setValue(1)
        slider.valueChanged.connect(self.slider_size_change)
        layout.addWidget(slider)

    def slider_size_change(self, value):
        self.canvas.set_brush_size(value)

    def add_buttons(self, layout):
        rect_b = QPushButton('🟨', self)
        rect_b.pressed.connect(lambda: self.canvas.change_tool('rect'))
        layout.addWidget(rect_b)
        circle_b = QPushButton('🟡', self)
        circle_b.pressed.connect(lambda: self.canvas.change_tool('ellipse'))
        layout.addWidget(circle_b)
        line_b = QPushButton('📏', self)
        line_b.pressed.connect(lambda: self.canvas.change_tool('line'))
        layout.addWidget(line_b)
        brush_b = QPushButton('🖌️', self)
        brush_b.pressed.connect(lambda: self.canvas.change_tool('brush'))
        layout.addWidget(brush_b)
        color_b = QPushButton('🎨', self)
        color_b.pressed.connect(self.show_color_picker)
        layout.addWidget(color_b)
        text_b = QPushButton('🅰️', self)
        text_b.pressed.connect(self.show_text_window)
        layout.addWidget(text_b)
        self.color_b = QPushButton('🔲',self)
        self.color_b.pressed.connect(self.fill)
        layout.addWidget(self.color_b)
        null_text = QLabel("", self)
        null_text.setMaximumSize(QtCore.QSize(10000, 24))
        layout.addWidget(null_text)

    def fill(self):
        if (self.canvas.fill):
            self.color_b.setText('🔲')
            self.canvas.fill = False
        else:
            self.color_b.setText('⬛️')
            self.canvas.fill = True
    
    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить рисунок", "", "PNG Image file (*.png)")
        if path:
            pixmap = self.canvas.pix
            pixmap.save(path, "PNG" )

class HelpWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Помощь")
        self.setWindowIcon(QIcon('icons/exclamation.ico'))
        self.text_edit = QTextEdit(self)
        self.text_edit.setStyleSheet("font-size: 10pt; font-family: Verdana;")
        self.text_edit.setReadOnly(True)
        self.setMinimumSize(QtCore.QSize(600,400))
        with open("documentation/doc.md", encoding="utf-8") as f:
            markdown_text = f.read()
        html = markdown.markdown(markdown_text)
        document = QTextDocument()
        document.setHtml(html)
        self.text_edit.setDocument(document)
        self.setCentralWidget(self.text_edit)

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()