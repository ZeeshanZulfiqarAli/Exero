import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

class MainWindow(qtw.QMainWindow):

    def __init__(self):
        super().__init__()
        # Main UI code goes here

        stylesheet = '''
        #qwid2{
            background-color: #FAFAFA;
            border: 0px solid red;
        }
        QMainWindow {
            background-color: #000000;
        }
        a{
            background-color: rgb(200,20,80);
        }
        '''
        stsheet2 = '''
        #lay2 {
            background-color: #FAFAFA;
        }
        #a{
            background-color: rgb(200,20,80);
        }

        '''
        self.setStyleSheet(stsheet2)
        
        self.x = qtw.QWidget(self)
        self.par = qtw.QHBoxLayout()
        self.x.setLayout(self.par)
        self.setCentralWidget(self.x)
        print(self.par.spacing())
        self.par.setSpacing(0)
        print(self.par.spacing())
        #self.par.insertSpacing(0,0)
        
        #grid_layout = qtw.QGridLayout()
        #qwidget = qtw.QWidget()
        #qwidget.setLayout(grid_layout)
        #self.setCentralWidget(qwidget)
        self.btn = qtw.QPushButton("<<")
        self.btn.setFixedWidth(25)
        label = qtw.QLabel("mje ande wala burger")
        btn2 = qtw.QPushButton("aam khaega?")
        #self.qwid2 = qtw.QWidget()
        lay2= qtw.QVBoxLayout()
        self.lw = qtw.QWidget()
        self.lw.setLayout(lay2)
        #self.qwid2.setLayout(lay2)
        #self.qwid2.setObjectName('qwid2')
        #self.qwid2.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)
        #self.qwid2.setMinimumSize(500,500)
        self.par.addWidget(self.lw)
        lay2.addWidget(label)
        lay2.addWidget(btn2)
        self.flag = True
        self.lw.setObjectName("lay2")
        
        #self.aw = qtw.QWidget()
        self.a = qtw.QVBoxLayout()
        self.aw = qtw.QWidget()
        self.aw.setLayout(self.a)
        print(self.a.spacing())
        self.a.setSpacing(0)
        print(self.a.spacing())
        self.par.addWidget(self.aw)
        self.a.setObjectName("a")
        #self.a.addWidget(qtw.QLabel("helllllooo"))
        self.a.addWidget(self.btn)
        #self.a.
        #print(self.lw.height(),self.lw.maximumHeight,self.lw.minimumHeight)
        
        #line_edit = qtw.QLineEdit("default value",self)
        #self.a.addWidget(line_edit)
        self.a.setContentsMargins(0,0,0,0)
        #self.lw.resizeEvent()
        #btn.setFixedHeight(self.lw.height())
        self.btn.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.MinimumExpanding)
        #self.par.addWidget(self.qwid2)
        #self.par.addWidget(self.aw)
        
        #grid_layout.addWidget(btn,0,1)
        #grid_layout.addWidget(self.qwid2,0,0)
        #grid_layout.setHorizontalSpacing
        #grid_layout.setHorizontalSpacing(0)
        #grid_layout.addWidget(btn2,1,0)
        self.btn.clicked.connect(self.onBtnClick)
        
        #btn.clicked.connect(btn2.setFixedWidth(0))
        # End main UI code)
        self.show()

    def onBtnClick(self):
        if self.flag:
            self.lw.setFixedWidth(0)
            self.btn.setText(">>")
        else:
            
            self.lw.setFixedWidth(80)
        self.flag = not(self.flag)

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
