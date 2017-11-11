import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class App(QDialog):
    def __init__(self):
        super().__init__()
        self.title = 'GoWithTheFlow - Browse File'
        self.left = 10
        self.top = 10
        self.width = 480
        self.height = 400
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createBrowseBar()

        buttonLoad = QPushButton('Go', self)
        buttonLoad.clicked.connect(self.go_pressed)

        self.dropArea = DropArea(textbox=self.textbox)
        self.dropArea.setMinimumSize(200, 200)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        windowLayout.addWidget(self.dropArea)
        windowLayout.addWidget(buttonLoad)
        self.setLayout(windowLayout)

        self.show()

    def createBrowseBar(self):
        self.horizontalGroupBox = QGroupBox("Browse filesystem:")
        layout = QHBoxLayout()

        self.textbox = QLineEdit(self)
        layout.addWidget(self.textbox)

        buttonBrowse = QPushButton('...', self)
        buttonBrowse.clicked.connect(self.browse_filesystem)
        layout.addWidget(buttonBrowse)

        self.horizontalGroupBox.setLayout(layout)
        self.horizontalGroupBox.setMaximumHeight(80)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Browse Filesystem", "",
                                                  "JPEG (*.jpg, *jpeg);;All Files (*)", options=options)
        return fileName

    @pyqtSlot()
    def browse_filesystem(self):
        filepath = self.openFileNameDialog()
        self.textbox.setText(filepath)
        pixmap = QPixmap(filepath)
        self.dropArea.setImage(pixmap)

    @pyqtSlot()
    def go_pressed(self):
        if not self.dropArea.getImage().isNull():
            print("go")


class DropArea(QLabel):
    changed = pyqtSignal(QMimeData)
    pixmap = None

    def __init__(self, parent=None, textbox=None):
        super(DropArea, self).__init__(parent)

        self.setMinimumSize(200, 200)
        self.setFrameStyle(QFrame.Sunken | QFrame.StyledPanel)
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)
        self.textbox = textbox
        self.clear()

    def dragEnterEvent(self, event):
        self.setText("Drop image here")
        self.setBackgroundRole(QPalette.Highlight)
        event.acceptProposedAction()
        self.changed.emit(event.mimeData())

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        mimeData = event.mimeData()

        if mimeData.hasImage():
            pixmap = QPixmap(mimeData.imageData())
            self.setImage(pixmap)
        elif mimeData.hasUrls():
            filepath = "\n".join([url.path() for url in mimeData.urls()])
            self.textbox.setText(filepath)
            pixmap = QPixmap(filepath)
            self.setImage(pixmap)
        else:
            self.textbox.setText("Cannot display data")

        self.setBackgroundRole(QPalette.Dark)
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.clear()
        event.accept()

    def clear(self):
        self.setText("Drop image here")
        self.setBackgroundRole(QPalette.Dark)
        self.changed.emit(None)

    def getImage(self):
        return self.pixmap

    def setImage(self, pixmap):
        self.pixmap = pixmap
        if pixmap.isNull():
            self.setText("Cannot display data")
        else:
            self.setPixmap(pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())