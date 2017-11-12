from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from image_renderer import ImageRenderer

class ColorBox(QWidget):
    def __init__(self, color):
        super().__init__()

        self.setFixedSize(24, 24)
        p = self.palette();
        p.setColor(QPalette.Background, color)
        self.setPalette(p)
        self.setAutoFillBackground(True)


class ResultsView(QWidget):
    def __init__(self, fileURL):
        super().__init__()

        self.colors = [
            Qt.red,
            Qt.yellow,
            Qt.green,
            Qt.blue
        ]
        self.imageRenderer = ImageRenderer(fileURL, self.colors)

        legendLayout = QVBoxLayout()
        legendLayout.setAlignment(Qt.AlignTop)
        self.colorLabels = []
        for color in self.colors:
            colorBox = ColorBox(color)
            colorLabel = QLineEdit()
            self.colorLabels.append(colorLabel)

            colorLayout = QHBoxLayout()
            colorLayout.addWidget(colorBox)
            colorLayout.addWidget(colorLabel)

            legendLayout.addLayout(colorLayout)
        calcButton = QPushButton('Calculate', self)
        calcButton.clicked.connect(self.calculate)
        legendLayout.addWidget(calcButton)

        self.statsLayout = QVBoxLayout()
        self.statsLayout.setAlignment(Qt.AlignTop)

        windowLayout = QHBoxLayout()
        windowLayout.addWidget(self.imageRenderer)
        windowLayout.addLayout(legendLayout)
        windowLayout.addLayout(self.statsLayout)
        self.setLayout(windowLayout)

    @pyqtSlot()
    def calculate(self):
        # Clear layout
        for i in reversed(range(self.statsLayout.count())):
            self.statsLayout.itemAt(i).widget().setParent(None)

        for colorLabel in self.colorLabels:
            label = QLabel(colorLabel.text())
            label.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
            label.setMinimumWidth(300)
            self.statsLayout.addWidget(label)
