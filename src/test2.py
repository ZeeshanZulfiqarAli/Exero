from PyQt5.QtCore import QPropertyAnimation, QRectF, QSize, Qt, pyqtProperty
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QColor, QBrush
from PyQt5.QtWidgets import (
    QAbstractButton,
    QApplication,
    QHBoxLayout,
    QSizePolicy,
    QWidget,
    QGraphicsDropShadowEffect
)


class Switch(QAbstractButton):
    def __init__(self, parent=None, track_radius=14, thumb_radius=11.245,widthScale = 1.0, heightScale = 1.0):
        # track_radius=10, thumb_radius=8
        super().__init__(parent=parent)
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        self.widthScale = widthScale
        self.heightScale = heightScale
        
        self._track_radius = (track_radius * self.widthScale)+0.5
        self._thumb_radius = (thumb_radius * self.widthScale)+0.5

        self._margin = max(0, self._thumb_radius - self._track_radius)
        self._base_offset = max(self._thumb_radius, self._track_radius)
        self._end_offset = {
            True: lambda: (0.35*(self.width() - 2 * self._margin))+(2.8*self.widthScale)+0.5, # 2
            False: lambda: self._base_offset,
        }
        self._offset = self._base_offset 
        self.setMinimumWidth((84.33 * self.widthScale)+0.5)#(60)
        palette = self.palette()
        if self._thumb_radius > self._track_radius:
            self._track_color = {
                True: palette.highlight(),
                False: palette.dark(),
            }
            self._thumb_color = {
                True: palette.highlight(),
                False: palette.light(),
            }
            self._text_color = {
                True: palette.highlightedText().color(),
                False: palette.dark().color(),
            }
            self._thumb_text = {
                True: '',
                False: '',
            }
            self._track_opacity = 0.5
        else:
            self._thumb_color = {
                True: QBrush(QColor("#BCBCBC")),
                False: QBrush(QColor("#BCBCBC")),
            }
            self._track_color = {
                True: QBrush(QColor("#7CCF7C")),
                False: QBrush(QColor("#E57272")),
            }
            self._text_color = {
                True: QColor("#F2F2F2"),
                False: QColor("#F2F2F2"),
            }
            self._thumb_text = {
                True: 'On',
                False: 'Off',
            }
            self._track_opacity = 1

    @pyqtProperty(int)
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        self.update()

    def sizeHint(self):  # pylint: disable=invalid-name
        #print()
        return QSize(
            4 * self._track_radius + 2 * self._margin,
            2 * self._track_radius + 2 * self._margin+ (5.6*self.widthScale)+0.5 , #4
        )

    def setChecked(self, checked):
        super().setChecked(checked)
        self.offset = self._end_offset[checked]()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.offset = self._end_offset[self.isChecked()]()
        #print("resize",self.offset)

    def paintEvent(self, event):  # pylint: disable=invalid-name, unused-argument
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(Qt.NoPen)
        track_opacity = self._track_opacity
        thumb_opacity = 1.0
        text_opacity = 1.0
        if self.isEnabled():
            track_brush = self._track_color[self.isChecked()]
            thumb_brush = self._thumb_color[self.isChecked()]
            text_color = self._text_color[self.isChecked()]
        else:
            track_opacity *= 0.8
            track_brush = self.palette().shadow()
            thumb_brush = self.palette().mid()
            text_color = self.palette().shadow().color()
        #print(type(text_color))
        p.setBrush(track_brush)
        p.setOpacity(track_opacity)
        path = QPainterPath()
        #p.setClipRect(0,0,80,80)
        
        path.addRoundedRect(
            self._margin + ((1.4*self.widthScale)+0.5), #self._margin + 1,
            self._margin + ((1.4*self.widthScale)+0.5), #self._margin + 1,
            self.width() -  ( 2 * self._margin )  -((2.8*self.widthScale)+0.5), #self.width() - 2 * self._margin -2,
            self.height() -  ( 2 * self._margin )  -((2.8*self.widthScale)+0.5), #self.height() - 2 * self._margin -2,
            self._track_radius +((2.8*self.widthScale)+0.5) , #self._track_radius +2 ,
            self._track_radius ,
        )
        #print(self.width() - ((2.8*self.widthScale)+0.5) * self._margin -((2.8*self.widthScale)+0.5),self.width() - (((2.8*self.widthScale)+0.5) * self._margin )-((2.8*self.widthScale)+0.5),(self.width() - ((2.8*self.widthScale)+0.5)) * (self._margin -((2.8*self.widthScale)+0.5)))
        p.fillPath(path,track_brush)
        p.setPen(QPen(QColor("#707070"),1))
        p.drawPath(path)
        
        #print("p.clipBoundingRect()",p.hasClipping())
        p.setPen(Qt.NoPen)
        '''p.drawRoundedRect(
            self._margin,
            self._margin,
            self.width() - 2 * self._margin ,
            self.height() - 2 * self._margin ,
            self._track_radius,
            self._track_radius,
        )'''
        p.setBrush(thumb_brush)
        p.setOpacity(thumb_opacity)
        '''p.drawEllipse(
            self.offset - self._thumb_radius,
            self._base_offset - self._thumb_radius,
            2 * self._thumb_radius,
            2 * self._thumb_radius,
        )'''
        #print(self._margin,self.width() - 2 * self._margin,self.height() - 2 * self._margin,self._track_radius)
        p.drawRoundedRect(
            self.offset - self._thumb_radius + ((2.8*self.widthScale)+0.5), #self.offset - self._thumb_radius + 2,
            self._base_offset - self._thumb_radius + ((2.8*self.widthScale)+0.5), #self._base_offset - self._thumb_radius + 2,
            0.65*(self.width() - 2 * self._margin),
            self.height() - 2 * self._margin - ((11.25*self.heightScale)+0.5), #self.height() - 2 * self._margin - 8,
            self._thumb_radius,
            self._thumb_radius,
        )
        #p.drawRect(0,0,1000,1000)
        
        p.setPen(text_color)
        p.setOpacity(text_opacity)
        font = p.font()
        font.setFamily("segoe ui")
        #print(font.family())
        font.setPixelSize(1.5 * self._thumb_radius)
        p.setFont(font)
        #print((self.width() - 2 * self._margin - 4)/2)
        '''p.drawText(
            QRectF(
                self.offset - self._thumb_radius + (self.width() - 2 * self._margin - 4)/2,
                self._base_offset - self._thumb_radius,
                2 * self._thumb_radius,
                2 * self._thumb_radius,
            ),
            Qt.AlignCenter,
            self._thumb_text[self.isChecked()],
        )'''
        if self.isChecked():
            x = (2.8*self.widthScale)+0.5 #2
        else:
            x = (2.8*self.widthScale)+0.5 #1
        p.drawText(
            QRectF(
            self.offset - self._thumb_radius + x,
            self._base_offset - self._thumb_radius,
            0.65*(self.width() - 2 * self._margin),
            self.height() - 2 * self._margin - 4
            ),
            Qt.AlignCenter,
            self._thumb_text[self.isChecked()],
        )
        #print(p.hasClipping(),p.clipRegion().isEmpty())
        #print("apple: ", self.x(),self.y(), self.width(), self.height())
        

    def mouseReleaseEvent(self, event):  # pylint: disable=invalid-name
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            anim = QPropertyAnimation(self, b'offset', self)
            anim.setDuration(120)
            anim.setStartValue(self.offset)
            anim.setEndValue(self._end_offset[self.isChecked()]())
            anim.start()

    def enterEvent(self, event):  # pylint: disable=invalid-name
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)


def main():
    app = QApplication([])

    # Thumb size < track size (Gitlab style)
    s1 = Switch()
    s1.toggled.connect(lambda c: print('toggled', c))
    s1.clicked.connect(lambda c: print('clicked', c))
    s1.pressed.connect(lambda: print('pressed'))
    s1.released.connect(lambda: print('released'))
    '''s2 = Switch()
    s2.setEnabled(False)

    # Thumb size > track size (Android style)
    s3 = Switch(thumb_radius=11, track_radius=8)
    s4 = Switch(thumb_radius=11, track_radius=8)
    s4.setEnabled(False)'''

    l = QHBoxLayout()
    l.addWidget(s1)
    #l.addWidget(s2)
    #l.addWidget(s3)
    #l.addWidget(s4)
    w = QWidget()
    w.setMinimumSize(QSize(500,500))
    w.setLayout(l)
    w.show()

    app.exec()


if __name__ == '__main__':
    main()