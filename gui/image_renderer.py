from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class ImageRenderer(QWidget):
    def __init__(self, fileURL, colors):
        super().__init__()

        self.BORDER_SIZE = 12
        self.OFFSET = 0

        self.zones = [
            ('top', 0, 300, colors[0]),
            ('top', 700, 900, colors[1]),
            ('left', 400, 800, colors[2]),
            ('bottom', 400, 600, colors[3])
        ]

        self.colors = colors
        self.colorIndex = 0

        self.drawingNewZone = False
        self.mousePressLocation = ()

        self.movingExistingZone = False
        self.moveZone = ()

        self.pixmap = QPixmap(fileURL)
        self.pixmap = self.pixmap.scaled(1200, 900, Qt.KeepAspectRatio)

        self.initUI()



    def initUI(self):
        self.setWindowTitle('GoWithTheFlow - Results')
        self.WIDTH = self.pixmap.width()
        self.HEIGHT = self.pixmap.height()
        self.setGeometry(100, 100, self.WIDTH + 2*self.BORDER_SIZE, self.HEIGHT + 2*self.BORDER_SIZE)
        self.show()

    def minimumSizeHint(self):
        return QSize(self.WIDTH + 2*self.BORDER_SIZE, self.HEIGHT + 2*self.BORDER_SIZE)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        painter.drawPixmap(QRect(self.BORDER_SIZE, self.BORDER_SIZE, self.pixmap.width(), self.pixmap.height()), self.pixmap)

        colorIndex = 0
        for zone in self.zones:
            painter.setPen(QPen(zone[3], self.BORDER_SIZE))
            self._paintZone(painter, zone)

        painter.end()

    def mousePressEvent(self, event):
        clickedZone = self._getClickedZone((event.x(), event.y()))
        if event.button() == Qt.LeftButton:
            self.mousePressLocation = (event.x(), event.y())
            if clickedZone == None:
                # Create new zone
                self.drawingNewZone = True
            else:
                # Move existing zone
                self.movingExistingZone = True
                self.moveZone = clickedZone
        else:
            # Delete clicked zone
            self.zones = [z for z in self.zones if z != clickedZone]
            self.update()


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            mouseReleaseLocation = (event.x(), event.y())
            if self.drawingNewZone:
                loc = self._getLoc(mouseReleaseLocation)
                self.zones.append(self._getZone(loc, mouseReleaseLocation))
                self.mousePressLocation = ()
                self.drawingNewZone = False
            elif self.movingExistingZone:
                # Calculate delta of the move
                delta = 0
                if self.moveZone[0] == 'left' or self.moveZone[0] == 'right':
                    delta = mouseReleaseLocation[1] - self.mousePressLocation[1]
                else:
                    delta = mouseReleaseLocation[0] - self.mousePressLocation[0]
                movedZone = (
                    self.moveZone[0],
                    self.moveZone[1] + delta,
                    self.moveZone[2] + delta,
                    self.moveZone[3]
                )
                self.zones = [z for z in self.zones if z != self.moveZone]
                self.zones.append(movedZone)

                self.mousePressLocation = ()
                self.moveZone = ()
                self.movingExistingZone = False
            self.update()

    def _paintZone(self, painter, zone):
        loc = zone[0]
        if loc == 'left':
            painter.drawLine(self.BORDER_SIZE/2, zone[1]+(self.BORDER_SIZE*3/2), self.BORDER_SIZE/2, zone[2]+(self.BORDER_SIZE/2))
        elif loc == 'right':
            painter.drawLine(self.WIDTH+(self.BORDER_SIZE*3/2), zone[1]+(self.BORDER_SIZE*3/2), self.WIDTH+(self.BORDER_SIZE*3/2), zone[2]+(self.BORDER_SIZE/2))
        elif loc == 'top':
            painter.drawLine(zone[1]+(self.BORDER_SIZE*3/2), self.BORDER_SIZE/2, zone[2]+(self.BORDER_SIZE/2), self.BORDER_SIZE/2)
        elif loc == 'bottom':
            painter.drawLine(zone[1]+(self.BORDER_SIZE*3/2), self.HEIGHT+(self.BORDER_SIZE*3/2), zone[2]+(self.BORDER_SIZE/2), self.HEIGHT+(self.BORDER_SIZE*3/2))


    def _getLoc(self, mouseReleaseLocation):
        deltaX = abs(self.mousePressLocation[0] - mouseReleaseLocation[0])
        deltaY = abs(self.mousePressLocation[1] - mouseReleaseLocation[1])
        if deltaY > deltaX:
            # Vertical (left or right)
            if mouseReleaseLocation[0] < self.BORDER_SIZE+(self.WIDTH/2):
                return 'left'
            else:
                return 'right'
        else:
            # Horizontal (top or bottom)
            if mouseReleaseLocation[1] < self.BORDER_SIZE+(self.HEIGHT/2):
                return 'top'
            else:
                return 'bottom'

    def _getClickedZone(self, mousePressLocation):
        x = mousePressLocation[0]
        y = mousePressLocation[1]
        for zone in self.zones:
            if 0 < x and x < self.BORDER_SIZE:
                # Left
                if zone[0] == 'left' and zone[1]+self.BORDER_SIZE < y and y < zone[2]+self.BORDER_SIZE:
                    return zone
            elif self.WIDTH + self.BORDER_SIZE < x and x < self.WIDTH + 2*self.BORDER_SIZE:
                # Right
                if zone[0] == 'right' and zone[1]+self.BORDER_SIZE < y and y < zone[2]+self.BORDER_SIZE:
                    return zone
            elif 0 < y and y < self.BORDER_SIZE:
                # Top
                if zone[0] == 'top' and zone[1]+self.BORDER_SIZE < x and x < zone[2]+self.BORDER_SIZE:
                    return zone
            elif self.HEIGHT + self.BORDER_SIZE < y and y < self.HEIGHT + 2*self.BORDER_SIZE:
                # Bottom
                if zone[0] == 'bottom' and zone[1]+self.BORDER_SIZE < x and x < zone[2]+self.BORDER_SIZE:
                    return zone


    def _getZone(self, loc, mouseReleaseLocation):
        if loc == 'left' or loc == 'right':
            zone = (
                loc,
                self.mousePressLocation[1]-self.BORDER_SIZE,
                mouseReleaseLocation[1]-self.BORDER_SIZE,
                self.colors[self.colorIndex]
            )
        else:
            zone = (
                loc,
                self.mousePressLocation[0]-self.BORDER_SIZE,
                mouseReleaseLocation[0]-self.BORDER_SIZE,
                self.colors[self.colorIndex]
            )
        self.colorIndex = (self.colorIndex + 1) % len(self.colors)
        return zone
