from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

class customSlider(qtw.QSlider):
    val = qtc.pyqtSignal(int)
    def __init__(self,animationStartValue,animationEndValue,QSS,minimum, maximum, animationDuration = 250,orientation=qtc.Qt.Horizontal,tip_offset=qtc.QPoint(0, -45),parent = None):
        super().__init__(parent,minimum = minimum, maximum = maximum, orientation = orientation)
        self.expectedValue = -1
        self.userChanging = False
        self.QSS = QSS
        self.tip_offset = tip_offset
        self.fps = None
        print("gotta here")
        
        self._animation = qtc.QVariantAnimation(
            self,
            valueChanged=self._animate,
            startValue=animationStartValue,
            endValue=animationEndValue,
            duration=animationDuration
        )

        self._animate(animationStartValue)

        self._style = self.style()
        self.opt = qtw.QStyleOptionSlider()

        #self.valueChanged.connect(self.show_tip)
        #self._animateWidth(5)
    
    def _animate(self, value):

        print("animate ",value)
        #self.heightFlag = True
        #self.newHeight = value
        #self.editAndSetStyleSheet()
        self.setStyleSheet(self.QSS.format(value.width(),value.height(),value.height()))
        

    def _animateWidth(self, value):

        print("animate ",value)
        self.widthFlag = True
        self.newWidth = value
        self.editAndSetStyleSheet()
        #self.setStyleSheet(self.QSS.format(value))
    
    def editAndSetStyleSheet(self):
        if self.heightFlag and self.widthFlag:
            self.setStyleSheet(self.QSS.format(self.newHeight,self.newHeight,self.newWidth))
            self.heightFlag = False
            self.widthFlag = False

    def enterEvent(self, event):
        #self.valueChanged.connect(self.show_tip)
        #self.setSliderDown(True)
        self._animation.setDirection(qtc.QAbstractAnimation.Forward)
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        #self.setSliderDown(False)
        
        #if self.receivers(self.valueChanged) > 0:
        #    self.valueChanged.disconnect(self.show_tip)
        self._animation.setDirection(qtc.QAbstractAnimation.Backward)
        self._animation.start()
        super().enterEvent(event)

    def mousePressEvent(self, ev):
        """ Jump to click position """
        self.oldV = self.value()
        self.userChanging = True
        self.setSliderDown(True)
        super().setValue(self.style().sliderValueFromPosition(self.minimum(), self.maximum(), ev.x(), self.width()))

    def mouseMoveEvent(self, ev):
        """ Jump to pointer position while moving """
        self.setSliderDown(True)
        super().setValue(self.style().sliderValueFromPosition(self.minimum(), self.maximum(), ev.x(), self.width()))
        self.setSliderDown(False)
    
    def mouseReleaseEvent(self, ev):

        self.val.emit(self.value())
        print("mouseReleaseEvent",self.oldV,self.value(),type(self.value()))
        self.expectedValue = self.value()+1
        self.setSliderDown(False)
        self.userChanging = False
        #alm

    def setValueManually(self,x,flag = True):
        '''works like mouse press event'''
        #tmp = self.style().sliderValueFromPosition(self.minimum(), self.maximum(), x, self.width())
        oldVal = self.userChanging
        self.userChanging = False
        tmp = x
        self.setValue(tmp)
        if flag:
            self.val.emit(tmp)
        print("x",x)
        self.userChanging = oldVal
    
    def setValue(self,v):
        #if not self.isSliderDown():
        if not self.userChanging:
            super().setValue(v)
        '''if v == self.expectedValue:
            self.expectedValue = -1
            print("bingo")
        elif self.expectedValue == -1:
            super().setValue(v)
        else:
            print("ignoring the values:",v,self.expectedValue)'''

    def setValueWithoutSignal(self,x):
        self.setValue(x)
        
    @qtc.pyqtSlot(int)
    def setFPS(self,fps):
        self.fps = fps

    def show_tip(self, _):
        self.initStyleOption(self.opt)
        rectHandle = self._style.subControlRect(self._style.CC_Slider, self.opt, self._style.SC_SliderHandle)
        print("rectHandle",rectHandle)
        pos_local = qtc.QPoint(rectHandle.topLeft().x() - (rectHandle.width()//2),rectHandle.topLeft().y() + self.tip_offset.y())
        pos_local = rectHandle.topLeft() + self.tip_offset
        print("pos_local",pos_local)
        pos_global = self.mapToGlobal(pos_local)
        if self.fps == None:
            text = "0:0"
        else:
            totalSecs = self.value()//self.fps
            mins = totalSecs//60
            secs = totalSecs%60
            text = str(mins)+":"+str(secs)

        qtw.QToolTip.showText(pos_global, text, self)