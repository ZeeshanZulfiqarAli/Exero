import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
#from .gui import MainWindow
#from . import splashScreen as ss
from . import gui
from . import resources

print("hello")


def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    #splash = ss.SplashScreen(":/splashscreen/frame.gif", flags=Qt.WindowStaysOnTopHint)
    #splash.show()
    app.processEvents()
    mw = gui.MainWindow()
    gui.setApp(app)
    
    #splash.finish(mw)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()