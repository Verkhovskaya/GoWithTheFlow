import sys
import subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from results_view import ResultsView

sys.path.append('../test/')
from run_detection import *

class App(QDialog):
    def __init__(self):
        super().__init__()
        self.title = 'GoWithTheFlow - Browse File'
        self.left = 100
        self.top = 100
        self.width = 480
        self.height = 400
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createBrowseBar()

        buttonLoad = QPushButton('Go', self)
        buttonLoad.clicked.connect(self.go_pressed)

        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab1, "Media Drop")
        self.tabs.addTab(self.tab2, "Video Preview")
        # self.tabs.setMinimumSize(400, 300)

        self.tab1.layout = QVBoxLayout(self)
        self.dropArea = DropArea(textbox=self.textbox)
        self.tab1.layout.addWidget(self.dropArea)
        self.tab1.setLayout(self.tab1.layout)

        self.tab2.layout = QVBoxLayout(self)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)

        self.tab2.layout.addWidget(videoWidget)
        self.tab2.layout.addLayout(controlLayout)

        self.tab2.setLayout(self.tab2.layout)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        windowLayout.addWidget(self.tabs)
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

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Browse Filesystem", "",
                                                  "MP4 (*.mp4);;All Files (*)", options=options)
        return fileName

    @pyqtSlot()
    def browse_filesystem(self):
        filepath = self.openFileNameDialog()
        self.textbox.setText(filepath)

        subprocess.run("ffmpeg -ss 00:00:00 -i {} -frames:v 1 tmp.jpg -y".format(filepath).split())

        pixmap = QPixmap("tmp.jpg")
        self.dropArea.setImage(pixmap)

    @pyqtSlot()
    def go_pressed(self):
        # if not self.dropArea.getImage().isNull():
        #     run_detection(self.textbox.displayText())
        #     self.dialog = ResultsView('tmp.jpg')
        #     self.dialog.show()
        self.dialog = ResultsView('C:/lined_img.png', 'C:/info.txt')
        self.dialog.show()

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            filepath = self.textbox.displayText()
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filepath)))
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

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
        self.setText("Drop video here")
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
            # This is really hacky
            if filepath[1:3] == 'C:':
                filepath = filepath[1:]
            print(filepath)
            self.textbox.setText(filepath)

            subprocess.run("ffmpeg -ss 00:00:00 -i {} -frames:v 1 tmp.jpg -y".format(filepath).split())

            pixmap = QPixmap("tmp.jpg")
            self.setImage(pixmap)
        else:
            self.textbox.setText("Cannot display data")

        self.setBackgroundRole(QPalette.Dark)
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.clear()
        event.accept()

    def clear(self):
        self.setText("Drop video here")
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
