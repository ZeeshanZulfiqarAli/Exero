from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtGui as qtg

class clickLabel(QLabel):
    clicked = pyqtSignal()
    def __init__(self,text = None, enterStyleSheet = None,leaveStyleSheet = None,a = False, boxColor = None, modifyStyleSheet = True,widthScale = 1.0, heightScale = 1.0, *args, **kwargs):
        self.enterStyleSheet = enterStyleSheet
        self.leaveStyleSheet = leaveStyleSheet
        self.widthScale = widthScale
        self.heightScale = heightScale
        if modifyStyleSheet:
            self.enterEvent = self.newEnterEvent
            self.leaveEvent = self.newLeaveEvent
        super().__init__(text,*args, **kwargs)
        if a:
            self.paintEvent=self.a
            self._boxColor = boxColor

    def mousePressEvent(self, ev):
        self.clicked.emit()

    def newEnterEvent(self,ev):
        if self.enterStyleSheet:
        #if self._underline:
            #self.setStyleSheet("#ctbLbl{text-decoration: underline;}")
            self.setStyleSheet(self.enterStyleSheet)
    
    def newLeaveEvent(self,ev):
        if self.leaveStyleSheet:
        #if self._underline:
            #self.setStyleSheet("#ctbLbl{text-decoration: none;}")
            self.setStyleSheet(self.leaveStyleSheet)

    def a(self,e):
        p = qtg.QPainter(self)
        p.setBrush(qtg.QBrush(self._boxColor))
        p.setPen(Qt.NoPen)
        p.setRenderHint(qtg.QPainter.Antialiasing, True)
        p.drawRect(0,0,(14.0556 * self.widthScale)+0.5,(14.0625 * self.heightScale)+0.5)#(0,0,10,10)
    
    def boxColor(self):
        return self._boxColor
    
    def setBoxColor(self, color):
        self._boxColor = color

    def click(self):
        self.clicked.emit()
    