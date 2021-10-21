import resources
import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

class MainWindow(qtw.QMainWindow):

    def __init__(self):
        super().__init__()
        # Main UI code goes here
        #F6F6F6
        stylesheet = """
        QMainWindow {
            background-color: #FAFAFA;
        }
        #label3,#label4 {
            font-family: Segoe UI;
            font-size: 22pt;
            color: #525856;
            font-weight: 200;
        }
        #label3 {
            font-size: 16pt;
        }
        #btn2{
            height: 30px;
            background-color: #F6F6F6;
            border-style: solid;
            border-color: #707070;
            border-width: 1px;
            border-radius: 15px;
            font-family: Segoe UI;
            font-size: 11pt;
            color: #424242;
        }
        #btn2:hover{
            background-color: #FCFCFC;
        }
        #btn2:pressed{
            background-color: #FFFFFF;
        }

        """
        self.setStyleSheet(stylesheet)
        self.setWindowTitle("Exero")
        #self.setWindowIcon(qtg.QIcon(':/icons/final_logo.svg'))
        #print(qtg.QIcon(':/icons/final_logo.svg').actualSize())
        #self.setWindowIcon()
        
        self.base_widget = qtw.QWidget()
        self.blayout = qtw.QVBoxLayout()
        self.base_widget.setLayout(self.blayout)
        self.setCentralWidget(self.base_widget)

        self.bookmark_add = qtg.QPixmap(':/icons/bookmark_add.svg')
        self.bookmark_remove = qtg.QPixmap(':/icons/bookmark_remove.svg')
        self.folder = qtg.QPixmap(':/icons/icons8-bookmark_add.svg')
        #self.folder = qtg.QPixmap(':/icons/bookmark_add.svg')
        self.final_logo = qtg.QPixmap(':/icons/final_fyp_logo2.svg')#.scaledToWidth(100,qtc.Qt.SmoothTransformation)
        self.setWindowIcon(qtg.QIcon(self.final_logo.scaledToWidth(50,qtc.Qt.SmoothTransformation)))

        self.logo_lbl = qtw.QLabel()
        self.logo_lbl.setPixmap(self.final_logo)
        '''
        self.bookmark_icon = qtg.QIcon()
        self.bookmark_icon.addPixmap(self.bookmark_remove, qtg.QIcon.Disabled)
        self.bookmark_icon.addPixmap(self.bookmark_add, qtg.QIcon.Active)
        self.button = qtw.QPushButton()
        
        self.button.setIcon(self.bookmark_icon)
        self.button.clicked.connect(lambda: self.button.setDisabled(self.isEnabled()) )
        '''
        self.btn = qtw.QPushButton("hello")
        self.btn.setObjectName('btn2')
        self.effect = qtw.QGraphicsDropShadowEffect()
        self.effect.setColor(qtg.QColor(194,207,161,204))
        self.effect.setBlurRadius(6)
        self.effect.setOffset(0,3)
        self.btn.setGraphicsEffect(self.effect)
        self.blayout.addWidget(self.btn)
        self.button_flag = False
        self.button = qtw.QPushButton()
        self.button.setObjectName('btn1')
        self.button.setIcon(qtg.QIcon(self.bookmark_add))
        self.button.clicked.connect(self.on_btn_click)
        self.l2 = qtw.QLabel("done bro")
        self.blayout.addWidget(self.l2)
        self.l2.setVisible(False)
        self.blayout.addWidget(self.button)
        self.blayout.addWidget(self.logo_lbl)
        self.label = click_Label("Apple")
        self.label.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.label.clicked.connect(lambda: self.l2.setVisible(True))
        #self.label2 = qtw.QLabel("<a href=\"#\" style=\"color: #525856; text-decoration:none; font-weight:200;\">Start detection on <span style=\"color: #D60404;\">live</span> video</a>")
        #self.label2.setObjectName("label2")
        #self.label2.linkActivated.connect(lambda: self.l2.setVisible(True))
        self.label2 = qtw.QLabel("<span style=\"color: #525856; font-family: segoe ui; font-size:22pt; font-weight:200;\">Start detection on <span style=\"color: #D60404;\">live</span> video</span>")
        self.label2.setObjectName("label2")
        self.label2.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.label3 = qtw.QLabel("Or")
        self.label3.setObjectName("label3")
        self.label4 = qtw.QLabel("Drag and drop pre-recorded video/image or click to browse")
        self.label4.setObjectName("label4")
        #self.toggle = qtw.Q
        self.blayout.addWidget(self.label2)
        self.blayout.addWidget(self.label3)
        self.blayout.addWidget(self.label4)
        self.blayout.addWidget(self.label)
        print(self.final_logo.width())
        # End main UI code
        self.show()

    def on_btn_click(self):
        if self.button_flag:
            self.button.setIcon(qtg.QIcon(self.bookmark_add))
        else:
            self.button.setIcon(qtg.QIcon(self.bookmark_remove))
        self.button_flag = not(self.button_flag)

class click_Label(qtw.QLabel):
    clicked = qtc.pyqtSignal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, ev):
        self.clicked.emit()

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
