from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from image_renderer import ImageRenderer
from parse import parse_txt
from random import *
from sklearn.cluster import KMeans
import numpy as np


class ColorBox(QWidget):
    def __init__(self, color):
        super().__init__()

        self.setFixedSize(24, 24)
        p = self.palette();
        p.setColor(QPalette.Background, color)
        self.setPalette(p)
        self.setAutoFillBackground(True)


class ResultsView(QWidget):
    def __init__(self, imageURL, dataURL):
        super().__init__()

        self.colors = [
            QColor(127,255,212),
            QColor(0,139,139),
            QColor(138,43,226),
            QColor(0,0,128),
            QColor(0,100,0),
            QColor(153,51,51)
        ]
        self.colorIndex = 0

        pixmap = QPixmap(imageURL)
        self.width = pixmap.width()
        self.height = pixmap.height()
        self.entrances, self.exits, self.zones = parse_txt(dataURL, self.width, self.height)
        print(self.zones)
        self._populateZonesWithColors()

        self.imageRenderer = ImageRenderer(imageURL, self.zones, self.colors, self.colorIndex)

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
        self.zones = self.imageRenderer.getZones()
        # Clear layout
        for i in reversed(range(self.statsLayout.count())):
            self.statsLayout.itemAt(i).widget().setParent(None)

        print(self.zones)
        print(self.getOpenings())
        exit_openings = self.reset_openings(self.entrances, self.getOpenings())
        entrance_openings = self.reset_openings(self.exits, self.getOpenings())
        # openings = [randint(0, len(self.zones)-1) for i in range(1, len(self.entrances + self.exits) + 1)]

        print(entrance_openings)
        print(exit_openings)

        o_to_name_mapping = []
        for i in range(len(self.zones)):
            color = self.zones[i][3]
            color_index = self.colors.index(color)
            name = self.colorLabels[color_index].text()
            o_to_name_mapping.append(name)

        path_hist = {}
        for i in range(len(self.entrances)):
            ent_o = o_to_name_mapping[entrance_openings[i]]
            ext_o = o_to_name_mapping[exit_openings[i]]
            if (ent_o, ext_o) not in path_hist:
                path_hist[(ent_o, ext_o)] = 0
            path_hist[(ent_o, ext_o)] += 1


        print(o_to_name_mapping)
        print(path_hist)

        for path in path_hist:
            print(path[0], path[1])
            if path[0] != path[1]:
                label = QLabel('{} to {}: {}'.format(path[0], path[1], path_hist[path]))
                label.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
                label.setMinimumWidth(300)
                self.statsLayout.addWidget(label)

    def reset_openings(self, ends, exits):
        exit_kmeans = KMeans(n_clusters=(len(exits)))

        exit_kmeans.cluster_centers_ = np.array(exits, dtype=int)

        y_vals = exit_kmeans.predict(ends)

        return y_vals

    def _populateZonesWithColors(self):
        augmented_zones = []
        for zone in self.zones:
            augmented_zones.append((
                zone[0], zone[1], zone[2],
                self.colors[self.colorIndex]
            ))
            self.colorIndex = (self.colorIndex + 1) % len(self.colors)
        self.zones = augmented_zones

    def getOpenings(self):
        openings = []
        for zone in self.zones:
            midpoint = (zone[2] + zone[1]) / 2
            if zone[0] == 'left':
                openings.append((0, midpoint))
            elif zone[0] == 'top':
                openings.append((midpoint, 0))
            elif zone[0] == 'right':
                openings.append((self.width, midpoint))
            elif zone[0] == 'bottom':
                openings.append((midpoint, self.height))
        return openings
