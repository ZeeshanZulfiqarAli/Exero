from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

class bookmarkWidget(QWidget):

    seekToFrameSignal = pyqtSignal(int)
    def __init__(self,parent = None):
        super().__init__(parent = None)
        self.seekToFrame = 0

    def mousePressEvent(self, ev):

        self.seekToFrameSignal.emit(self.seekToFrame)