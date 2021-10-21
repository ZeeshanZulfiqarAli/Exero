import resources
import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

class MainWindow(qtw.QMainWindow):

    def __init__(self):
        super().__init__()
        # Main UI code goes here
        
        self.setWindowTitle("Exero")
        #self.setWindowIcon()
        
        self.base_widget = qtw.QWidget()
        self.blayout = qtw.QVBoxLayout()
        self.base_widget.setLayout(self.blayout)
        self.setCentralWidget(self.base_widget)

        self.bookmark_add = qtg.QPixmap(':/icons/bookmark_add.svg')
        self.bookmark_remove = qtg.QPixmap(':/icons/bookmark_remove.svg')
        self.folder = qtg.QPixmap(':/icons/icons8-bookmark_add.svg')
        #self.folder = qtg.QPixmap(':/icons/bookmark_add.svg')
        self.final_logo = qtg.QPixmap(':/icons/final_logo.svg').scaledToWidth(75,qtc.Qt.SmoothTransformation)

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
        self.button_flag = False
        self.button = qtw.QPushButton()
        self.button.setIcon(qtg.QIcon(self.bookmark_add))
        self.button.clicked.connect(self.on_btn_click)
        self.l2 = qtw.QLabel("done bro")
        self.blayout.addWidget(self.l2)
        self.l2.setVisible(False)
        self.blayout.addWidget(self.button)
        self.blayout.addWidget(self.logo_lbl)
        self.label = click_Label("Apple")
        self.label.clicked.connect(lambda: self.l2.setVisible(True))
        self.label2 = qtw.QLabel("<a href=\"#\">Start detection on live video</a>")
        self.blayout.addWidget(self.label2)
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
