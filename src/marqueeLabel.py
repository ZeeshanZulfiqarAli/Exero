from random import randrange

from PyQt5.QtCore import Qt, pyqtProperty, QTimer, QAbstractAnimation, QTimeLine, QSize, QPointF, QPoint
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QPainter, QStaticText, QTransform, QImage, qRgba, QColor, qRed, QRgba64, qRgb, QGradient, \
	QLinearGradient, QBrush, QFontMetricsF


# based on https://stackoverflow.com/a/10655396/160630 - thanks!

class marqueeLabel(QLabel):

	def __init__(self, parent=None):
		super(marqueeLabel, self).__init__(parent)
		self.staticText = QStaticText()
		self.staticText.setTextFormat(Qt.PlainText)
		self._string = ''
		self.timer = QTimer()
		self.timer.setInterval(16)
		self.timer.setTimerType(Qt.PreciseTimer)
		self.timer.timeout.connect(self.timerTimeout)
		self.waitTimer = QTimer()
		self.waitTimer.setInterval(3000)
		self.waitTimer.timeout.connect(self.timerTimeout)
		self.leftMargin = self.height() / 3
		#print("self.leftMargin",self.leftMargin,self.maximumWidth())
		self.scrollPos = 0
		self.buffer = QImage()
		self.alphaChannel = QImage()
		self.scrollEnabled = False
		self.waiting = True
		self.flag = True
		self.seperator = ' -- '
		self.updateText()
		self.wholeTextSize = QSize(0,0)

	def text(self):
		return self._string

	def setText(self, string):
		self._string = string
		#r = self.rect()
		#self.wholeTextSize = QSize(r.width(),r.height())
		self.updateText()
		self.update()
		self.updateGeometry()

	def sizeHint(self):
		return QSize(min(self.wholeTextSize.width() + self.leftMargin, self.maximumWidth()),
					 self.fontMetrics().height())

	def updateText(self):
		self.timer.stop()
		#print(self._string)
		
		self.singleTextWidth = self.fontMetrics().width(self._string)
		self.scrollEnabled = self.singleTextWidth > self.width() - self.leftMargin

		if self.scrollEnabled:

			self.staticText.setText(self._string + self.seperator)
			self.setToolTip(self._string)
			if not self.window().windowState() & Qt.WindowMinimized:
				self.scrollPos = 0
				self.waitTimer.start()
				self.waiting = True
		else:
			self.staticText.setText(self._string)
		#print("st text",self.staticText.text())
		#a = QFontMetricsF(self.fontMetrics()).boundingRect(self.staticText.text())
		#a.setWidth(300)
		#b = QFontMetricsF(self.fontMetrics()).boundingRect(a,0,self.staticText.text())
		#print("self.fontMetrics().width(self.staticText.text()",QFontMetricsF(self.fontMetrics()).width(self.staticText.text()),self.singleTextWidth,self.width(),self.fontMetrics().horizontalAdvance("This is one heck of a long text --"),self.fontMetrics().size(Qt.TextSingleLine,self.staticText.text()),self.fontMetrics().boundingRect(self.staticText.text()),a,b)

		self.staticText.prepare(QTransform(), self.font())
		self.wholeTextSize = QSize(QFontMetricsF(self.fontMetrics()).width(self.staticText.text()),
								   QFontMetricsF(self.fontMetrics()).height())
		#self.wholeTextSize = QSize(self.getRect().width(),self.getRect().height())


	# self.setFixedWidth()

	def hideEvent(self, event):
		if self.scrollEnabled:
			self.scrollPos = 0
			self.timer.stop()
			self.waitTimer.stop()

	def showEvent(self, event):
		if self.scrollEnabled:
			self.waitTimer.start()
			self.waiting = True

	def paintEvent(self, paintevent):
		painter = QPainter(self)
		if self.flag:
			self.r = painter.boundingRect(0,0,0,0,0,self.staticText.text())
			self.wholeTextSize = QSize(self.r.width(),self.r.height())
			self.flag = False
		if self.scrollEnabled:
			self.buffer.fill(qRgba(0, 0, 0, 0))
			pb = QPainter(self.buffer)
			pb.setPen(painter.pen())
			pb.setFont(painter.font())
			#print("self.wholeTextSize.width() a",self.wholeTextSize.width())
			x = min(-self.scrollPos, 0) + self.leftMargin
			#print("x",x)
			while x < self.width():
				pb.drawStaticText(QPointF(x, (self.height() - self.wholeTextSize.height()) / 2), self.staticText)
				x += self.wholeTextSize.width()
				#x += self.width()
				#print("xx",x,self.width(),)
			# apply Alpha channel
			pb.setCompositionMode(QPainter.CompositionMode_DestinationIn)
			pb.setClipRect(self.width() - 15, 0, 15, self.height())
			pb.drawImage(0, 0, self.alphaChannel)
			pb.setClipRect(0, 0, 15, self.height())
			pb.drawImage(0, 0, self.alphaChannel)
			painter.drawImage(0, 0, self.buffer)
		else:
			painter.drawStaticText(QPointF(self.leftMargin,
										   (self.height() - self.wholeTextSize.height()) / 2),
								   self.staticText)

	def resizeEvent(self, resizeEvent):
		# When the widget is resized, we need to update the alpha channel.
		self.alphaChannel = QImage(self.size(), QImage.Format_ARGB32_Premultiplied)
		self.buffer = QImage(self.size(), QImage.Format_ARGB32_Premultiplied)
		self.alphaChannel.fill(qRgba(0, 0, 0, 0))
		self.buffer.fill(qRgba(0, 0, 0, 0))
		if self.width() > 64:
			grad = QLinearGradient(QPointF(0, 0), QPointF(16, 0))
			grad.setColorAt(0, QColor(0, 0, 0, 0))
			grad.setColorAt(1, QColor(0, 0, 0, 255))
			painter = QPainter(self.alphaChannel)
			painter.setBrush(grad)
			painter.setPen(Qt.NoPen)
			painter.drawRect(0, 0, 16, self.height())
			grad = QLinearGradient(QPointF(self.alphaChannel.width() - 16, 0),
								   QPointF(self.alphaChannel.width(), 0))
			grad.setColorAt(0, QColor(0, 0, 0, 255))
			grad.setColorAt(1, QColor(0, 0, 0, 0))
			painter.setBrush(grad)
			painter.drawRect(self.alphaChannel.width() - 16, 0, self.alphaChannel.width(), self.height())
			# filename = 'alphaChannel'+str(randrange(0, 100000))+'.png'
			# print('writing '+filename)
			# self.alphaChannel.save(filename, 'PNG')
		else:
			self.alphaChannel.fill(QColor(0, 0, 0))

		newScrollEnabled = (self.singleTextWidth > self.width() - self.leftMargin)
		if not newScrollEnabled == self.scrollEnabled:
			self.updateText()

	def timerTimeout(self):
		self.scrollPos = (self.scrollPos + 1) % \
						 (self.wholeTextSize.width())
		#print("self.wholeTextSize.width() b",self.wholeTextSize.width())
		if self.waiting == True:
			self.waiting = False
			self.timer.start()
			self.waitTimer.stop()
		elif self.scrollPos == 0:
			self.waiting = True
			self.timer.stop()
			self.waitTimer.start()

		self.update()