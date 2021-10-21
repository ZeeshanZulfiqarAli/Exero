'''import PyQt5QApplication>
import <QLabel>
import <QBitmap>'''
'''from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import sys
 
#QApplication app(argc, argv)
app = qtw.QApplication(sys.argv)
lbl = qtw.QLabel()
pixmap=qtg.QPixmap(r"D:\zeeshan work\fyp gui\Exero\exero\yell.png")
lbl.setPixmap(pixmap)
lbl.setMask(pixmap.mask())
lbl.setWindowFlags(qtc.Qt.SplashScreen | qtc.Qt.FramelessWindowHint)
lbl.show()
app.setQuitOnLastWindowClosed(True)
print("done")
app.exec()
'''

import sys
import os
from . import settings
from . import svgEditor
from PyQt5 import QtCore, QtGui, QtWidgets     # + QtWidgets

from PyQt5.QtWidgets import QApplication, QLabel, QSplashScreen, QWidget, QVBoxLayout, QFrame
from PyQt5.QtCore    import QTimer, Qt, QRect
from PyQt5.QtGui    import QPixmap, QBitmap, QMovie, QPainter, QBrush, QPen, QColor
#import resources


class customQMovie(QMovie):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        print("i am here")

    def paintEvent(self,ev):
        #super().paintEvent(self,ev)
        print(self.currentFrameNumber())

class customQSplashScreen(QSplashScreen):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def paintEvent(self, ev):
        super().paintEvent(ev)
        print(movie.currentFrameNumber())
        print("i am here")
        
        self.p = QPainter()
        self.p.begin(self)
        self.p.setRenderHint(QPainter.Antialiasing, True)
        #self.p.setPen(Qt.NoPen)
        #self.p.setBrush(Qt.NoBrush)
        
        self.p.drawPixmap(0,0,pixmap)
        #self.p.drawPixmap(151,114,movie.currentPixmap())
        self.p.end()

class SplashScreen(QSplashScreen):
    def __init__(self, animation, flags, msg=''):
        QSplashScreen.__init__(self, QPixmap(), flags)
        self.movie = QMovie(animation)
        self.movie.setCacheMode(QMovie.CacheAll)
        self.movie.frameChanged.connect(self.onNextFrame)
        self.settings = settings.getObj()

        if getattr(sys, 'frozen', False):
            directory = sys._MEIPASS
        else: # Not frozen
            directory = os.path.dirname(__file__)
        
        self.svgEditor = svgEditor.svgEditor(os.path.join(directory,"splashScreen.svg"),self.settings.value("boxColor","#FFFFFF",str),None)
        self.svgEditor.process()
        self.basePixmap = QPixmap(os.path.join(directory,"splashScreen.svg"))
        self.flag = False
        self.counter = 0
        self.bColor = QColor("#FFFFFF")
        self.rectColor = QColor("#FAFAFA")
        self.bboxColor = QColor(self.settings.value("boxColor","#FFFFFF",str))
        self.movie.start()
        self.showMessage(msg, Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        self.show()

    #@pyqtSlot()
    def onNextFrame(self):
        pixmap = self.movie.currentPixmap()
        self.counter += 1
        print(self.counter)
        self.p = QPainter(self.basePixmap)
        self.p.begin(self)
        self.p.setRenderHint(QPainter.Antialiasing, True)
        self.p.setPen(Qt.NoPen)
        self.p.setBrush(QBrush(self.bColor, Qt.SolidPattern))   #Qt.SolidPattern
        width = (self.counter/229)*707    # TO-DO: replace (self.counter/229) with the percentage of work done. like someObjRef.getPercentage()
        self.p.drawRect(38,479,width,20)    #707
        self.p.setBrush(Qt.NoBrush)
        
        self.p.drawPixmap(151,114,pixmap)
        #self.p.drawPixmap(151,114,movie.currentPixmap())
        # draw rect with color of background on the left and right side of the GIF
        self.p.setBrush(QBrush(self.rectColor, Qt.SolidPattern))
        self.p.drawRect(151,114,39,360)
        self.p.drawRect(592,114,39,360)
        self.p.setBrush(Qt.NoBrush)
        fnum = self.movie.currentFrameNumber()
        
        if fnum>=140 or (fnum<20 and self.flag):
            self.flag = True
            #self.p.setPen(QPen(Qt.black, 5, Qt.SolidLine))
            #self.bboxColor = QColor("#FFFFFF")
            if fnum>150 or fnum<=20:
                if fnum<20:
                    fnum += 161
                #self.opacity = (1-(fnum/180)) *4
                self.opacity = (180-fnum)/30
            else:
                self.opacity = 1
            self.bboxColor.setAlphaF(self.opacity)
            self.p.setPen(QPen(self.bboxColor, 5, Qt.SolidLine))
            self.p.setBrush(Qt.NoBrush)
            #print(self.p.isActive())
            self.p.setRenderHint(QPainter.Antialiasing, True)

            self.p.drawRect(261+151,265+114,90,90)
        self.p.end()
        self.setPixmap(self.basePixmap)

class customQLabel(QLabel):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.flag = False
        if getattr(sys, 'frozen', False):
            directory = sys._MEIPASS
        else: # Not frozen
            directory = os.path.dirname(__file__)
        
        #self.bg = QPixmap(r"D:\splashScreen.svg")
        self.bg = QPixmap(os.path.join(directory,"splashScreen.svg"))
        #self.bg = QPixmap(r"D:\zeeshan work\fyp gui\Exero\exero\expand.svg")

    def paintEvent(self,ev):
        
        #super().paintEvent(ev)
        self.p = QPainter()
        self.p.begin(self)
        self.p.setRenderHint(QPainter.Antialiasing, True)
        self.p.setPen(Qt.NoPen)
        self.p.setBrush(Qt.NoBrush)
        self.p.drawPixmap(0,0,self.bg)
        self.p.drawPixmap(151,114,movie.currentPixmap())
        self.p.end()
        fnum = movie.currentFrameNumber()
        #print(fnum)
        if fnum>=140 or (fnum<20 and self.flag):
            self.flag = True
            self.p = QPainter()
            self.p.begin(self)
            #self.p.setPen(QPen(Qt.black, 5, Qt.SolidLine))
            self.color = QColor("#FFFFFF")
            if fnum>150 or fnum<=20:
                if fnum<20:
                    fnum += 161
                #self.opacity = (1-(fnum/180)) *4
                self.opacity = (180-fnum)/30
            else:
                self.opacity = 1
            self.color.setAlphaF(self.opacity)
            self.p.setPen(QPen(self.color, 5, Qt.SolidLine))
            self.p.setBrush(Qt.NoBrush)
            #print(self.p.isActive())
            self.p.setRenderHint(QPainter.Antialiasing, True)

            self.p.drawRect(261+151,265+114,90,90)
            self.p.end()
            #print("self.paintingActive",self.paintingActive())


# TRY TO MAKE A CUSTOM CLASS FOR SPLASH SCREEN AND PUT EVERYTHING IN ITS PAINT EVENT


if __name__ == '__main__':
    app = QApplication(sys.argv)
    print("done bro")
    #label = QLabel()

    #pixmap=QPixmap(r"D:\zeeshan work\fyp gui\Exero\exero\test.png")
    #pixmap=QPixmap(r"D:\splashScreen1.svg")
    #pixmap.setMask(QBitmap(r"D:\zeeshan work\fyp gui\Exero\exero\2(2).bmp"))
    #print(pixmap.hasA)
    #label.setPixmap(pixmap)
    #wid = QWidget()
    #lay = QVBoxLayout()
    #wid.setLayout(lay)
    #gifLbl = customQLabel()
    #gifLbl.setStyleSheet("QLabel{background-color: rgba(255,255,0,0%);}")
    #gifLbl.setFrameStyle(QFrame.NoFrame)
    #gifLbl.setGeometry(QRect(0,0,750,504)) #151,149.5
    #label.setGeometry(QRect(0,0,750,504)) #151,149.5
    #movie = QMovie(r"D:\frame0000_2.gif")
    #gifLbl.setMovie(movie)
    #label.setMovie(movie)
    #lay.addWidget(gifLbl)
    #splash = QSplashScreen(label,pixmap, flags=Qt.WindowStaysOnTopHint)
    #splash = QSplashScreen(gifLbl, flags=Qt.WindowStaysOnTopHint)
    
    #lay.addWidget(label)
    #movie.start()
    #splash = customQSplashScreen(wid, flags=Qt.WindowStaysOnTopHint)
    splash = SplashScreen(":/splashscreen/frame.gif", flags=Qt.WindowStaysOnTopHint)
    #print(splash.windowFlags())
    #splash.setAttribute(Qt.WA_TranslucentBackground)
    
    splash.show()
    app.processEvents()
    
    #print(pixmap.mask())
    #label.setMask(pixmap.mask())
    #label.setMask(QBitmap(r"D:\zeeshan work\fyp gui\Exero\exero\2(2).bmp"))

    # SplashScreen - Indicates that the window is a splash screen. This is the default type for .QSplashScreen
    # FramelessWindowHint - Creates a borderless window. The user cannot move or resize the borderless window through the window system.
    #label.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
    #label.show()

    #gifLbl.setWindowFlags(Qt.SplashScreen |  Qt.WindowStaysOnTopHint)
    #wid.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
    #wid.show()
    #gifLbl.show()
    #movie.start()

    # Automatically exit after  5 seconds
    QTimer.singleShot(10000, app.quit) 
    sys.exit(app.exec_())