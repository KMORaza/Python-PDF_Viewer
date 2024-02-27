import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QSlider, QScrollArea, QAction, QMenuBar, QStatusBar, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QImage, QPixmap
import fitz  
class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.setWindowTitle('PDF Viewer')
        self.setGeometry(100, 100, 1500, 1200)  
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.image_label = QLabel(self)
        self.scroll_area.setWidget(self.image_label)
        self.layout.addWidget(self.scroll_area)
        self.slider_zoom = QSlider(Qt.Horizontal)
        self.slider_zoom.setMinimum(1)
        self.slider_zoom.setMaximum(500)
        self.slider_zoom.setValue(200)
        self.slider_zoom.valueChanged.connect(self.updateZoom)
        self.layout.addWidget(self.slider_zoom)
        self.doc = None
        self.current_page = 0
        self.createMenuBar()
        self.createToolBar()
        self.createStatusBar()
    def createMenuBar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('📁')
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.openPDF)
        file_menu.addAction(open_action)
        zoom_in_action = QAction('+🔍', self)
        zoom_in_action.triggered.connect(self.zoomIn)
        menubar.addAction(zoom_in_action)
        zoom_out_action = QAction('-🔍', self)
        zoom_out_action.triggered.connect(self.zoomOut)
        menubar.addAction(zoom_out_action)
    def createToolBar(self):
        toolbar = self.addToolBar('Navigation')
        previous_action = QAction('◀', self)
        previous_action.triggered.connect(self.previousPage)
        toolbar.addAction(previous_action)
        next_action = QAction('▶', self)
        next_action.triggered.connect(self.nextPage)
        toolbar.addAction(next_action)
    def createStatusBar(self):
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)
    def openPDF(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog  
        file_name, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if file_name:
            self.displayPDF(file_name)
    def displayPDF(self, file_path):
        doc = fitz.open(file_path)
        self.doc = doc
        self.current_page = 0
        self.updatePage()
    def updateZoom(self, value):
        zoom_factor = value / 100.0
        self.updatePage(zoom_factor)
    def updatePage(self, zoom_factor=2.0):
        if self.doc is not None and 0 <= self.current_page < len(self.doc):
            page = self.doc[self.current_page]
            image = page.get_pixmap(matrix=fitz.Matrix(zoom_factor, zoom_factor))
            q_image = QImage(image.samples, image.width, image.height, image.stride, QImage.Format_RGB888)
            pixmap = QPixmap(q_image)
            self.image_label.setPixmap(pixmap)
        statusbar = self.statusBar()
        statusbar.showMessage(f'Page {self.current_page + 1} of {len(self.doc)}')
    def zoomIn(self):
        current_value = self.slider_zoom.value()
        self.slider_zoom.setValue(min(current_value + 30, self.slider_zoom.maximum()))
    def zoomOut(self):
        current_value = self.slider_zoom.value()
        self.slider_zoom.setValue(max(current_value - 10, self.slider_zoom.minimum()))
    def wheelEvent(self, event):
        if self.doc is not None:
            num_steps = event.angleDelta().y() / 120
            if num_steps > 0 and self.current_page > 0:
                self.current_page -= 1
                self.updatePage()
            elif num_steps < 0 and self.current_page < len(self.doc) - 1:
                self.current_page += 1
                self.updatePage()
    def previousPage(self):
        if self.doc is not None and self.current_page > 0:
            self.current_page -= 1
            self.updatePage()
    def nextPage(self):
        if self.doc is not None and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.updatePage()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec_())
