import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

class MainWindow(qtw.QMainWindow):

    def __init__(self):
        super().__init__()
        # Main UI code goes here
        stylesheet = """
        QMainWindow {
            background-color: #FAFAFA;
        }
        #label,#label {
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
        }"""
        
        stsheet2 = '''
        
        #label{
            font-family: segoe ui;
            font-size: 22pt;
            color: #525856;
            font-weight: 200;
        }
        '''
        # Set window related properties
        self.setStyleSheet(stsheet2)
        self.x = qtw.QLabel(" .")
        self.x.setFixedWidth(0)
        #self.label = qtw.QLabel("<span style=\"color: #525856; font-family: segoe ui; font-size:22pt; font-weight:200;\">Sample Text</span>")
        self.label = qtw.QLabel("Sample Text")
        self.label.setObjectName("label")
        self.label2 = qtw.QLabel("<span style=\"color: #525856; font-family: segoe ui; font-size:22pt; font-weight:200;\">Sample Text 2</span>")
        self.baseWidget = qtw.QWidget(self)
        self.baseLayout = qtw.QHBoxLayout()
        self.baseWidget.setLayout(self.baseLayout)
        self.setCentralWidget(self.baseWidget)
        
        self.baseLayout.addWidget(self.x)
        self.baseLayout.addWidget(self.label)
        self.baseLayout.addWidget(self.label2)

        
        #print("done")
        self.show()

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
